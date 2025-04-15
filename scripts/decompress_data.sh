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

# decompress all files ending in .tar.gz
for file in $(ls $path); do
    if [ -f $path/$file ] && [[ $file == *.tar.gz ]]; then
        # decompress the file
        echo "Decompressing $path/$file"
        tar -xzf $path/$file -C $path
        # remove the file
        echo "Removing $path/$file"
        rm $path/$file

        echo ""
    fi
done

echo "All files decompressed"