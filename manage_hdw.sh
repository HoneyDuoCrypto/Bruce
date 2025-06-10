#!/bin/bash
# HDW Management Script

case "$1" in
    start)
        echo "🚀 Starting HDW services..."
        sudo systemctl start hdw-tunnel.service
        sudo systemctl start hdw-web.service
        echo "✅ HDW services started"
        echo "🌐 Access: https://hdw.honey-duo.com"
        ;;
    stop)
        echo "🛑 Stopping HDW services..."
        sudo systemctl stop hdw-web.service
        sudo systemctl stop hdw-tunnel.service
        echo "✅ HDW services stopped"
        ;;
    restart)
        echo "🔄 Restarting HDW services..."
        sudo systemctl restart hdw-tunnel.service
        sleep 3
        sudo systemctl restart hdw-web.service
        echo "✅ HDW services restarted"
        echo "🌐 Access: https://hdw.honey-duo.com"
        ;;
    status)
        echo "📊 HDW Service Status:"
        echo ""
        echo "🚇 Tunnel Service:"
        sudo systemctl --no-pager status hdw-tunnel.service
        echo ""
        echo "🌐 Web Service:"
        sudo systemctl --no-pager status hdw-web.service
        echo ""
        echo "🔗 Access: https://hdw.honey-duo.com"
        ;;
    logs)
        echo "📋 HDW Service Logs:"
        echo ""
        echo "🚇 Tunnel Logs (last 20 lines):"
        sudo journalctl -u hdw-tunnel.service -n 20 --no-pager
        echo ""
        echo "🌐 Web Logs (last 20 lines):"
        sudo journalctl -u hdw-web.service -n 20 --no-pager
        ;;
    *)
        echo "🍯 HDW Management Script"
        echo "======================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start HDW services"
        echo "  stop    - Stop HDW services"  
        echo "  restart - Restart HDW services"
        echo "  status  - Show service status"
        echo "  logs    - Show recent logs"
        echo ""
        echo "🌐 Access: https://hdw.honey-duo.com"
        ;;
esac
