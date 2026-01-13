#!/bin/bash
# Start script voor PDOK Postcode Opzoeker Web Interface

echo "=========================================="
echo "PDOK Postcode Opzoeker - Web Interface"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is niet geïnstalleerd"
    echo "   Download van: https://www.python.org/downloads/"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is niet geïnstalleerd"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment aanmaken..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Virtual environment activeren..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📥 Dependencies installeren..."
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p uploads results

# Start the application
echo ""
echo "🚀 Server starten..."
echo "   Toegankelijk op: http://localhost:5000"
echo "   Stop met Ctrl+C"
echo ""

python3 app.py
