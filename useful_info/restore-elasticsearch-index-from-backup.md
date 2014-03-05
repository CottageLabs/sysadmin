#Warning
ALWAYS REFER TO THE SCRIPT FOR THE LATEST USAGE INFO! (It could be updated independently of this file)

This is just for convenience.

#Example of using the restore script:

    /opt/sysadmin/backup/restore_from_s3.sh s3://yonce-index-backup /opt/elasticsearch/data /home/cloo/backups/elasticsearch/

#Usage reminder


3 arguments needed
Usage: ```./restore_from_s3.sh s3://<bucket_name> <restore_to_dir> <local_restore_dir_with_trailing_slash>```

All files and folders in your S3 bucket will be:
  1. synced down from your S3 bucket (only changed ones and new ones will be downloaded) to ```<local_restore_dir_with_trailing_slash>```
  2. they will then be copied (only changed and new ones) from ```<local_restore_dir_with_trailing_slash>``` to ```<restore_to_dir>```
  (No attempts at decompression will be made)

#s3cmd configuration

If the following error occurs:

```
ERROR: /home/cloo/.s3cfg: No such file or directory
ERROR: Configuration file not available.
ERROR: Consider using --configure parameter to create one.
```

then copy the .s3cfg file from another server. It's got private AWS credentials so it can't be held in the sysadmin repo.

##copying .s3cfg securely

1. SSH into a server which has it (e.g. yonce).
2. Generate a private key using ssh-keygen, use the usual CL server password as the passphrase. (NOTE: YOU REALLY SHOULD PROTECT IT WITH A PASSPHRASE!)
3. cat ~/.ssh/id_rsa.pub
4. append the result of the previous command to the ~/.ssh/authorized_keys on the target (your new) server
5. scp ~/.s3cfg cloo@188.226.163.151:/home/cloo  # replace the IP address with the address of the target (your new) server

    The key should be protected with the usual CL server password. Ask Mark or Emanuil if you don't know it.
