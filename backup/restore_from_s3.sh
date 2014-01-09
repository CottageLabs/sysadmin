#!/bin/bash

if [ $# -ne 3 ]
then
    echo "3 arguments needed"
    echo "Usage: $0 s3://<bucket_name> <restore_to_dir> <local_restore_dir_with_trailing_slash>"
    echo
    echo "All files and folders in your S3 bucket will be:"
    echo "  1. synced down from your S3 bucket (only changed ones and new ones will be downloaded) to <local_restore_dir_with_trailing_slash>"
    echo "  2. they will then be copied (only changed and new ones) from <local_restore_dir_with_trailing_slash> to <restore_to_dir>"
    echo "  (No attempts at decompression will be made)"
    exit 1
fi

bucket=$1
restore_to_dir=$2
local_restore_dir=$3

if [[ $bucket != s3://* ]]; then
    echo "Your bucket name must be prefixed by s3://"
    echo "Remember, \"explicit is better than implicit.\" -- Tim Peters"
    exit 1
fi

# need to run rsync as root in order to preserve root permissions and modification times
s3cmd sync -H --acl-private --no-delete-removed "$bucket" "$local_restore_dir"
sudo rsync -aEhv "$local_restore_dir" "$restore_to_dir"
