##### BASIC SETUP #####
# this may be needed - not sure, seems to work without it
#export DEBIAN_FRONTEND=noninteractive

# create user - DO THIS MANUALLY, AND GIVE THE USER A PASSWORD
# REMEMBER TO UPLOAD SOME PUBLIC KEYS BEFORE CHANGING THE SSH SETTINGS
# adduser --gecos "" XXX-USERNAME-HERE-XXX
# and set the pw at the prompt
# (there is a usual CL username and password, but they are not stored here ...)
cd /home/cloo
mkdir /home/cloo/.ssh
chown cloo:cloo /home/cloo/.ssh
chmod 700 /home/cloo/.ssh
# and copy required pubkeys into it
# If you are creating a new Digital Ocean droplet and have specified
# keys to be included on the DO control panel, do this:
# cp /root/.ssh/authorized_keys .ssh/
# chown cloo:cloo .ssh/authorized_keys

# If you wish to add more keys manually:
# vim /home/cloo/.ssh/authorized_keys
chown cloo:cloo /home/cloo/.ssh/authorized_keys
chmod 600 /home/cloo/.ssh/authorized_keys
# if version ubuntu 12.04 - previous to that the group was admin 
adduser cloo sudo
# visudo and set cloo ALL=(ALL) NOPASSWD: ALL at the end

# prevent "unknown host" message when doing sudo
# regular user version: sudo sh -c 'echo "127.0.1.1       "`cat /etc/hostname` >> /etc/hosts'
# but if you're root (should be at this point of script)
echo "127.0.1.1       "`cat /etc/hostname` >> /etc/hosts

# make some oft-used backup dirs
mkdir -p /home/cloo/backups/elasticsearch
mkdir -p /home/cloo/backups/elasticsearch-es-exporter
mkdir -p /home/cloo/backups/logs
mkdir -p /home/cloo/cron-logs
chown -R cloo:cloo /home/cloo/backups

# time
sudo apt-get -q -y install ntp
sudo dpkg-reconfigure tzdata  # Europe/London

# edit the ssh settings
vim /etc/ssh/sshd_config
# change it as follows:
PermitRootLogin no
PasswordAuthentication no
/etc/init.d/ssh restart

# set up firewall - allow 22, 80, 443
apt-get -q -y install ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable

# set up newrelic server monitoring
echo "deb http://apt.newrelic.com/debian/ newrelic non-free" >> /etc/apt/sources.list.d/newrelic.list
wget -O- https://download.newrelic.com/548C16BF.gpg | apt-key add -
apt-get update
apt-get install newrelic-sysmond
nrsysmond-config --set license_key=<license key>
sudo service newrelic-sysmond start
# go to https://rpm.newrelic.com/accounts/526071/server_alert_policies
# and assign your new server to the appropriate policy


# apt install useful stuff
add-apt-repository -y ppa:webupd8team/java
apt-get update
# pre-accept the Oracle Java binaries license
echo "debconf shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
echo "debconf shared/accepted-oracle-license-v1-1 seen true" | debconf-set-selections
apt-get -q -y install mcelog bpython screen htop nginx git-core curl anacron sysv-rc-conf s3cmd bc vnstat python-pip python-dev python-setuptools build-essential python-software-properties oracle-java7-installer

# run java -version from the command line to check java's version
# additionally ps and htop will show you the exact path to the java executable running elasticsearch, which includes the version number

# Set up s3cmd to access the CL AWS account
# scp <existing server>:/home/cloo/.s3cfg .
# scp .s3cfg <new server>:/home/cloo
# rm .s3cfg

# If you can't find a prefilled config file, do this:
# s3cmd --configure # take Access and Secret keys it asks for from Cottage Labs' AWS account at amazon.cottagelabs.com

##### PYTHON AND SUPERVISOR #####

# pip install useful python stuff
pip install --upgrade pip
ln -s /usr/local/bin/pip /usr/bin/pip
pip install --upgrade virtualenv
pip install gunicorn
pip install requests


# get latest version of supervisor via pip
pip install supervisor
curl -s https://raw.githubusercontent.com/Supervisor/initscripts/eb55c1a15d186b6c356ca29b6e08c9de0fe16a7e/ubuntu > ~/supervisord
mv ~/supervisord /etc/init.d/supervisord
chmod a+x /etc/init.d/supervisord
/usr/sbin/service supervisord stop
update-rc.d supervisord defaults
mkdir /var/log/supervisor
mkdir /etc/supervisor/
mkdir /etc/supervisor/conf.d

# Path below relative to this script!
cp config/supervisor/supervisord.conf /etc/supervisor/supervisord.conf

ln -s /etc/supervisor/supervisord.conf /etc/supervisord.conf
ln -s /usr/local/bin/supervisord /usr/bin/supervisord
/usr/sbin/service supervisord start


##### OPTIONAL SETUP #####

# get new elasticsearch, 1.4.4 (now available as 1.5.x and later, so if you 
# think you're better off with  a newer one, check ES' website for the right link)
java -version  # make sure you are happy with what this returns, otherwise upgrade it
wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.4.4.deb
sudo dpkg -i elasticsearch-1.4.4.deb

# to run on boot, ES recommends
# sudo update-rc.d elasticsearch defaults 95 10
# sudo /etc/init.d/elasticsearch start
# We generally use sysv-rc-conf for the more intuitive UI, but feel free to use whichever.
sudo sysv-rc-conf  # select "elasticsearch" for runlevels 2-5

sudo vim /etc/default/elasticsearch
# set
# ES_HEAP_SIZE=1g  # or about half the RAM on the server if RAM is up to 8GB. Feel free to set to 12GB if RAM is 16GB. Remember a large disk cache enhances ES performance, so don't just allocate all the RAM to ES' heap. And obviously you may need RAM for other things.
# MAX_LOCKED_MEMORY=unlimited
# RESTART_ON_UPGRADE=false

sudo vim /etc/elasticsearch/elasticsearch.yml
# set
# bootstrap.mlockall: true
# discovery.zen.ping.multicast.enabled: false

# It's a wise idea to disable public access to ES
sudo ufw deny in on eth0 to any port 9200
sudo ufw deny in on eth0 to any port 9300
sudo ufw status  # check rules and that firewall is active
# This still leaves the private network and localhost:9200 functional

sudo service elasticsearch restart  # you should be done. Check with curl localhost:9200 and htop that ES is running and taking the memory you expect.

### RESTORING FROM ES 1.x BACKUPS

# install the ES S3 plugin
curl -s "localhost:9200/_nodes/settings?pretty=true" | grep "home"  # find out where elasticsearch's executable files live
cd /usr/share/elasticsearch  # usually /usr/share/elasticsearch with the ES .deb package, but amend as per the grep result above this line if needed

# Find out which version of the plugin you need for your ES here:
# https://github.com/elastic/elasticsearch-cloud-aws#aws-cloud-plugin-for-elasticsearch
sudo bin/plugin install elasticsearch/elasticsearch-cloud-aws/2.4.2
sudo service elasticsearch restart

# register the backup repo
curl -XPUT 'http://localhost:9200/_snapshot/{BACKUP_REPO_NAME}' -d '{
    "type": "s3",
    "settings": {
        "bucket": "{YOUR BUCKET}",
        "region": "{YOUR REGION, usually eu-west-1 for CL}",
        "access_key": "{the ES AWS access key - one PER PROJECT}",
        "secret_key": "{the ES AWS secret key - one PER PROJECT}"
    }
}'
# Make your own restricted AWS user for each project! Ask ET how, or see
# https://github.com/elastic/elasticsearch-cloud-aws#recommended-s3-permissions if making your own.

# You should get {"acknowledged":true} after the command above.

# See all available snapshots for restore
# curl localhost:9200/_snapshot/doaj_s3/_all?pretty=true

curl -XPOST "http://localhost:9200/_snapshot/{SNAPSHOT_REPO}/{SPECIFIC_SNAPSHOT}/_restore"
# You should get {"accepted":true} to that.
# After that until the restore completes (at about 15MiB/s in ET's experience) you can look at how far it's gone by doing
# curl -s localhost:9200/_status?pretty=true | grep "primary_size_in_bytes" && date

# After your restore finishes, if this is a TEST MACHINE, you should delete the repository so that you don't accidentally write to it
curl -XDELETE "localhost:9200/_snapshot/doaj_s3"


# get elasticsearch 0.90.7 - old instructions for pre-1.x ES
cd /opt
curl -L https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.7.tar.gz -o elasticsearch.tar.gz
tar -xzvf elasticsearch.tar.gz
ln -s elasticsearch-0.90.7 elasticsearch
rm elasticsearch.tar.gz
cd elasticsearch/bin
git clone git://github.com/elasticsearch/elasticsearch-servicewrapper.git
cd elasticsearch-servicewrapper
git checkout 0.90
mv service ../
cd ../
rm -R elasticsearch-servicewrapper
ln -s /opt/elasticsearch/bin/service/elasticsearch /etc/init.d/elasticsearch
update-rc.d elasticsearch defaults
# elasticsearch settings
# vim config/elasticsearch.yml and uncomment bootstrap.mlockall: true
# and uncomment cluster.name: elasticsearch (and change cluster name if necessary)
# IMPORTANT!!! put
# script.disable_dynamic: true
# at the end of the config/elasticsearch.yml file! This is to prevent DDoS-ing
# others through our ES and locking up of the server by our ISP if port 9200 is
# open...
# OK, now:
# vim bin/service/elasticsearch.conf and set.default.ES_HEAP_SIZE=4096 or whatever value works for the machine
# then vim /etc/security/limits.conf and put this in:
# root  hard  nofile  1024000
# root  soft  nofile  1024000
# root  hard  memlock unlimited
# root  soft  memlock unlimited
# * hard  nofile  1024000
# * soft  nofile  1024000
# * hard  memlock unlimited
# * soft  memlock unlimited
# and then vim /etc/pam.d/common-session and /etc/pam.d/common-session-noninteractive
# and put the following in it:
# session required      pam_limits.so
sudo /etc/init.d/elasticsearch start
# this command will always tell you "Running with PID XXX". Even though plugins could cause it to fail to start. So wait for 15 seconds, then try
# curl localhost:9200
# you should get a response, otherwise something's wrong, check /opt/elasticsearch/logs.


# install node
apt-get install python-software-properties g++ make
apt-add-repository ppa:chris-lea/node.js
apt-get update
apt-get install nodejs
npm install sqlite3

mkdir /home/cloo/elasticsearch-exporter-src
cd /home/cloo/elasticsearch-exporter-src
npm install elasticsearch-exporter --production
cd /home/cloo
ln -s elasticsearch-exporter-src/node_modules/elasticsearch-exporter/exporter.js elasticsearch-exporter
chown -R cloo:cloo elasticsearch-exporter*


# install php stuff
#apt-get install php5 php5-cli php5-mysql php5-cgi
#add-apt-repository ppa:brianmercer/php
#apt-get update
#apt-get install php5-fpm


# install mysql stuff
#apt-get install mysql-server libmysqlclient-dev python-mysqldb
#pip install mysql-python


# installing etherpad lite
# http://mclear.co.uk/2011/08/01/install-etherpad-lite-on-ubuntu/
# https://github.com/Pita/etherpad-lite/wiki/How-to-deploy-Etherpad-Lite-as-a-service
#apt-get install build-essential python libssl-dev libsqlite3-dev gzip curl
#cd /opt
#git clone git://github.com/Pita/etherpad-lite.git
#useradd etherpad-lite
#mkdir /var/log/etherpad-lite
#chown -R etherpad-lite:etherpad-lite /var/log/etherpad-lite
#chown -R etherpad-lite:etherpad-lite /opt/etherpad-lite
#cd /etc/init.d
#vim etherpad-lite # and copy the script from the above linked page into it, and customise
# e.g. change the path to link to where node is on this install - /usr/bin/node/bin
# and the eplite dir - 
#chmod +x etherpad-lite
#update-rc.d etherpad-lite defaults
#cd /opt/etherpad-lite
# edit the settings.json - change db type to sqlite and db file to var/sqlite.db


# set up sensors package for better monitoring and more information e.g. CPU temperatures
# THIS IS POINTLESS ON VIRTUAL SERVERS
# taken from https://help.ubuntu.com/community/SensorInstallHowto
# 1. apt-get install lm-sensors
# 2. Run sudo sensors-detect and choose YES to all YES/no questions.
# 3. At the end of sensors-detect, a list of modules that needs to be loaded will displayed. Type "yes" to have sensors-detect insert those modules into /etc/modules, or edit /etc/modules yourself.
# 4. Next, run
# sudo service module-init-tools restart
# This will read the changes you made to /etc/modules in step 3, and insert the new modules into the kernel.
# See sensor info by running "sensors" from the shell.


