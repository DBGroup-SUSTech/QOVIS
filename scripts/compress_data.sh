#!/bin/bash

dataset=$1

if [ -z "$dataset" ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

path="../qovis_backend/data/$dataset/raw"
# to abs path
path=$(realpath $path)
# don't keep the trailing slash
path=${path%/}

# compress all folders
for folder in $(ls $path); do
    if [ -d $path/$folder ]; then
        # compress the folder
        echo "Compressing $path/$folder"
        tar -czf $path/$folder.tar.gz -C $path $folder
        # remove the folder
        echo "Removing $path/$folder"
        rm -rf $path/$folder

        echo ""
    fi
done

echo "All files compressed"