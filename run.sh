#!/bin/bash

if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Please install pip before continuing."
    exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error installing dependencies."
    exit 1
fi

echo "Running main.py..."
nohup python main.py &

if [ $? -ne 0 ]; then
    echo "Error running main.py."
    exit 1
else
    echo "Bot started successfully!"
fi