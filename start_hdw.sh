#!/bin/bash
echo "🍯 Starting HDW Professional Interface..."
echo "🌐 Public URL: https://hdw.honey-duo.com"
echo "🔐 Login: hdw / HoneyDuo2025!"
echo ""

# Start tunnel service
sudo systemctl start hdw-tunnel.service
echo "✅ Tunnel started"

# Wait a moment for tunnel to connect
sleep 3

# Start web interface
echo "🌐 Starting web interface..."
python3 hdw_secure.py
