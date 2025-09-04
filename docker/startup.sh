#!/bin/bash
# Startup script for NanoQuant Enterprise services

echo "🚀 Starting NanoQuant Enterprise services..."

# Start Enterprise API server in background
echo "Starting Enterprise API server..."
python -m nanoquant.api.enterprise_endpoints &

# Start Admin dashboard in background
echo "Starting Admin dashboard..."
streamlit run nanoquant/admin/dashboard.py &

# Start nginx
echo "Starting nginx proxy..."
nginx -g "daemon off;"