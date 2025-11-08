#!/bin/bash
# Quick test script for the printer maintenance application
# This script helps test the application without Docker

set -e

echo "=========================================="
echo "Printer Maintenance Application Test"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Set default environment variables for testing
export PRINTER_IP="${PRINTER_IP:-192.168.1.100}"
export NTFY_CHANNEL="${NTFY_CHANNEL:-printer-test}"
export PRINTER_NAME="${PRINTER_NAME:-HP Smart Tank 7005}"
export SNMP_COMMUNITY="${SNMP_COMMUNITY:-public}"
export OUTPUT_PATH="${OUTPUT_PATH:-/tmp/printer-test.pdf}"

echo "Configuration:"
echo "  PRINTER_IP: $PRINTER_IP"
echo "  NTFY_CHANNEL: $NTFY_CHANNEL"
echo "  PRINTER_NAME: $PRINTER_NAME"
echo "  SNMP_COMMUNITY: $SNMP_COMMUNITY"
echo "  OUTPUT_PATH: $OUTPUT_PATH"
echo ""

# Run the application
echo "Running printer maintenance application..."
echo "=========================================="
cd src && python3 main.py

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Test completed successfully!"
    echo "Generated PDF: $OUTPUT_PATH"
else
    echo "❌ Test failed with exit code: $EXIT_CODE"
fi
echo "=========================================="

exit $EXIT_CODE
