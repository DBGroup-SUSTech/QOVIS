#!/bin/bash

dataset=$1

if [ -z "$dataset" ]; then
    echo "Usage: $0 <dataset>"
    echo "Example: $0 data_preset"
    exit 1
fi

cd ../qovis_backend
source venv/bin/activate

python3.9 parser/spliter_exec.py -d $dataset
python3.9 parser/trace_extractor_exec.py -d $dataset
python3.9 parser/transform_search_exec.py -d $dataset

echo "Data preprocessing done"