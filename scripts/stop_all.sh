#!/bin/bash

# kill if the process is still running
if [ "$(lsof -t -i:14000)" ]; then
    echo "Kill backend"
    kill -9 $(lsof -t -i:14000)
fi

if [ "$(lsof -t -i:14001)" ]; then
    echo "Kill frontend"
    kill -9 $(lsof -t -i:14001)
fi

# check if the process is still running
if [ "$(lsof -t -i:14000)" ]; then
    echo "Backend still running"
fi

if [ "$(lsof -t -i:14001)" ]; then
    echo "Frontend still running"
fi

echo "Done"
