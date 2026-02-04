Index ES 7.10 to OS 1.3

## New OpenSearch Index machines:

$208 / month 3xSSD memory optimised.

			Public IP		Private IP
doaj-search-rw1 	134.209.28.121          10.131.22.203
doaj-search-rw2 	138.68.133.201          10.131.99.251
doaj-search-r1  	206.189.29.94           10.131.100.180
doaj-search-r2  	167.71.136.148          10.131.124.133

### Install OpenSearch via ansible

	ansible-playbook -i doaj-hosts.ini provision/install_opensearch_playbook.yml

### Customise the `opensearch.yml` and `jvm.options` files

Note, we are provisioning 2 clusters, `doaj-rw` and `doaj-r` (for leader and follower), `cluster.name` and `discovery.seed_hosts` should differ

```diff
$ diff opensearch.yml opensearch.default.yml
17c17
< cluster.name: doaj-rw
---
> #cluster.name: my-application
23c23
< node.name: ${HOSTNAME}
---
> #node.name: node-1
43c43
< bootstrap.memory_lock: true
---
> #bootstrap.memory_lock: true
55c55
< network.host: _eth1:ipv4_
---
> #network.host: 192.168.0.1
68,69c68
<                      # doaj-search-rw1   doaj-search-rw2
< discovery.seed_hosts: ["10.131.22.203", "10.131.99.251"]
---
> #discovery.seed_hosts: ["host1", "host2"]
114,120d112
<
< ## Carried from DOAJ Elasticsearch:
< http.cors.enabled: true
< http.cors.allow-origin: "*"
< http.cors.allow-methods: OPTIONS, HEAD, GET, POST, PUT, DELETE
< http.cors.allow-headers: X-Requested-With,X-Auth-Token,Content-Type,Content-Length
< http.cors.allow-credentials: true
```

Set the jvm.options to use half of system memory:

```diff
$ diff jvm.options jvm.options.default
22,23c22,23
< -Xms16g
< -Xmx16g
---
> -Xms1g
> -Xmx1g
```

Ensure we have our limits set

`sudo systemctl edit opensearch`

Note the file must be edited at the top, between the comments shown below.

```
### Anything between here and the comment below will become the contents of the drop-in file

[Service]
LimitMEMLOCK=infinity
LimitNOFILE=65535

### Edits below this comment will be discarded
...
```

Then reload opensearch with:

	sudo systemctl daemon-reload
	sudo systemctl restart opensearch

Check connectivity:

```
$ curl -k https://admin:admin@10.131.22.203:9200

{
  "name" : "doaj-search-rw1",
  "cluster_name" : "doaj-rw",
  "cluster_uuid" : "lHC7lM3OSUe3F1LFpHWMFA",
  "version" : {
    "distribution" : "opensearch",
    "number" : "1.3.20",
    "build_type" : "deb",
    "build_hash" : "31afd17a1b5a22338307e1f4a78092887c1490e3",
    "build_date" : "2024-12-11T19:27:27.239674Z",
    "build_snapshot" : false,
    "lucene_version" : "8.10.1",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "The OpenSearch Project: https://opensearch.org/"
}
```

Disable security due to 'Security Plugin Not Initialised'

add to `opensearch.yml`:
```
# To keep equivalence with ES OSS as deployed
plugins.security.disabled: true
```


Inform the cluster which nodes are master eligible (temporarily)

Replace the setting in `opensearch.yml` and restart, then comment-out and restart again.

```
cluster.initial_master_nodes:
  - doaj-search-rw1
  - doaj-search-rw2
```

### Set up cross-cluster replication (on doaj-r cluster)

Note, I've removed the use_roles parts since security is disabled.

```
curl -XPUT -H 'Content-Type: application/json' '10.131.100.180:9200/_cluster/settings?pretty' -d '
{
  "persistent": {
    "cluster": {
      "remote": {
        "replicate-doaj-rw": {
          "seeds": ["10.131.22.203:9300", "10.131.99.251:9300"]
        }
      }
    }
  }
}'

curl -XPOST -k -H 'Content-Type: application/json' '10.131.100.180:9200/_plugins/_replication/_autofollow?pretty' -d '
{
   "leader_alias" : "replicate-doaj-rw",
   "name": "replicate-doaj-all",
   "pattern": "doaj-*"
}'
```

### Getting the data

Install S3 backup plugin on all nodes on `doaj-rw` (we won't need to back up the follower):

	sudo -u opensearch /usr/share/opensearch/bin/opensearch-plugin install repository-s3

Add config to `opensearch.yml`

```
# Settings for Backups
s3.client.default.endpoint: "s3.eu-west-2.amazonaws.com"
s3.client.default.max_retries: 5
s3.client.default.use_throttle_retries: true
s3.client.default.region: "eu-west-2"
```

Insert keys in the store

	sudo -u opensearch /usr/share/opensearch/bin/opensearch-keystore add s3.client.default.access_key
	sudo -u opensearch /usr/share/opensearch/bin/opensearch-keystore add s3.client.default.secret_key

Setup the old/source backup repo as read-only

```
curl -XPUT '10.131.22.203:9200/_snapshot/doaj-index-ipt-backups' --header 'Content-Type: application/json' -d '{
    "type":"s3",
    "settings": {
        "bucket":"doaj-index-ipt-backups",
        "server_side_encryption":"true",
        "readonly":"true"
    }
}'
```

Check we have the backups listed after `{"acknowledged":true}` (doaj-search-rw2)

	curl 10.131.99.251:9200/_snapshot/doaj-index-ipt-backups/_all?pretty

Register new opensearch snapshots repository (will switch to this)

```
curl -XPUT '10.131.99.251:9200/_snapshot/doaj-opensearch-backups' --header 'Content-Type: application/json' -d '{
    "type":"s3",
    "settings": {
        "bucket":"doaj-opensearch-backups",
        "server_side_encryption":"true",
        "compress":"true"
    }
}'
```

Restore the latest snapshot

	curl -XPOST 10.131.99.251:9200/_snapshot/doaj-index-ipt-backups/2026-02-03_2319z/_restore


Get the status of our recovery from snapshot

	curl '10.131.22.203:9200/_recovery?human&pretty'

It's also helpful to grep for `stage` to see how many shards are `DONE` and how many are in `INDEX` state (i.e. incomplete)


Watch the index counts and indexes go from yellow to green:

	watch -n 10 -d 'curl -s 10.131.22.203:9200/_cat/indices | sort'


Issue a new snapshot in our `doaj-opensearch-backups` bucket

	curl -XPUT 10.131.99.251:9200/_snapshot/doaj-opensearch-backups/2026-02-04_0130z/


