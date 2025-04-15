#!/bin/bash

dataset=$1

if [ -z "$dataset" ]; then
    echo "Usage: $0 <dataset>"
    echo "Example: $0 data_preset"
    exit 1
fi

# backend
if [ "$(lsof -t -i:14000)" ]; then
    echo "Kill backend"
    kill -9 $(lsof -t -i:14000)
fi
cd ../qovis_backend
source venv/bin/activate
nohup python3.9 ./server/app.py -d $1 2>&1 &
deactivate
echo "Backend started"

# frontend
if [ "$(lsof -t -i:14001)" ]; then
    echo "Kill frontend"
    kill -9 $(lsof -t -i:14001)
fi
cd ../qovis_frontend
nohup npm run serve-dev 2>&1 &
echo "Frontend started"
