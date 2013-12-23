#!/bin/bash

now=`date +%Y-%m-%d_%H%M`
backup_file_suffix=".tar.gz"

if [ $# -ne 4 ]
then
    echo "4 arguments needed"
    echo "Usage: $0 <dir_or_file_to_backup> <local_backup_dir_with_trailing_slash> <backup_filename_prefix> s3://<bucket_name>"
    echo
    echo "The local backup file will then be called:"
    echo "  <backup_dir_with_trailing_slash><backup_filename_prefix>_<current_time>$backup_file_suffix"
    echo
    echo "If you are backing up a directory, <backup_filename_prefix> will be ignored and all files and folders in your directory will be:"
    echo "  1. copied to the <local_backup_dir_with_trailing_slash"
    echo "  2. sync-ed with your S3 bucket (only changed ones and new ones will be uploaded)"
    echo "  (No compression will be applied to directories)"
    exit 1
fi

dir_or_file_to_backup=$1
backup_dir=$2
backup_file_prefix=$3
bucket=$4

if [[ $bucket != s3://* ]]; then
    echo "Your bucket name must be prefixed by s3://"
    echo "Remember, \"explicit is better than implicit.\" -- Tim Peters"
    exit 1
fi

if [[ -d $dir_or_file_to_backup ]]; then
    whatisit="dir"
else
    whatisit="file"
fi

if [ $whatisit == "dir" ]; then
    rsync -uaEhv "$dir_or_file_to_backup" "$backup_dir"
    s3cmd sync --acl-private --no-delete-removed "$backup_dir" "$bucket"
else
    tar -zcf "$backup_dir""$backup_file_prefix"_"$now""$backup_file_suffix" "$dir_or_file_to_backup"
    s3cmd sync --acl-private --no-delete-removed "$backup_dir""$backup_file" "$bucket"
fi

