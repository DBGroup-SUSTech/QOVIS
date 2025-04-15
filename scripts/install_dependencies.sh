#!/bin/bash

# backend
cd ../qovis_backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
echo "Backend dependencies installed"

# frontend
cd ../qovis_frontend
npm install
echo "Frontend dependencies installed"

echo "Dependencies installation done"
