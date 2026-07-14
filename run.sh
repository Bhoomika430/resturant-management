#!/bin/bash

echo "=========================================="
echo "   BakBak Cafe - Restaurant Management"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 is not installed!"
    echo "Please install Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Mac: brew install python3"
    exit 1
fi

echo "[1/4] Python found!"
python3 --version

# Install dependencies
echo ""
echo "[2/4] Checking dependencies..."
pip3 install -r requirements.txt

# Start the server
echo ""
echo "[3/4] Starting BakBak Cafe server..."
echo ""
echo "=========================================="
echo "   OPEN BROWSER: http://localhost:5000"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
