# Quick Reference

## Common Commands

### Docker
```bash
# Start the container
docker-compose up -d

# View logs in real-time
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Run maintenance manually
docker exec hp-printer-maintenance /usr/local/bin/python /app/main.py

# View cron job logs
docker exec hp-printer-maintenance tail -f /var/log/printer-maintenance.log

# Access container shell
docker exec -it hp-printer-maintenance /bin/bash
```

### Local Testing
```bash
# Run test script
./test.sh

# Test imports only
cd src && python3 -c "from config import Config; from snmp_collector import SnmpCollector; from pdf_generator import PdfGenerator; from ipp_printer import IppPrinter; from notification import Notifier"

# Run main application
cd src && python3 main.py

# Test PDF generation
cd src && python3 pdf_generator.py
```

### Environment Variables
```bash
# Required
export PRINTER_IP=192.168.1.100
export NTFY_CHANNEL=printer-maintenance

# Optional
export PRINTER_NAME="HP Smart Tank 7005"
export SNMP_COMMUNITY=public
export OUTPUT_PATH=/tmp/printer-test.pdf
export TZ=America/New_York
```

## Cron Schedule Examples

Edit `Dockerfile` line 31 to change schedule:

```bash
# Daily at 3:00 AM
0 3 * * *

# Every Monday at 9:00 AM
0 9 * * 1

# Twice weekly (Monday & Thursday at 2:00 AM)
0 2 * * 1,4

# Every 6 hours
0 */6 * * *
```

Format: `minute hour day month weekday`

## Troubleshooting

### Check printer connectivity
```bash
ping 192.168.1.100
```

### Test SNMP access
```bash
docker exec hp-printer-maintenance snmpwalk -v2c -c public 192.168.1.100 system
```

### Test IPP printing
```bash
docker exec hp-printer-maintenance lpstat -h 192.168.1.100 -p
```

### View generated PDF
```bash
ls -lh /tmp/printer-output/printer-test.pdf
```

### Check container health
```bash
docker ps
docker inspect hp-printer-maintenance
```

## File Locations

### In Container
- Application: `/app/`
- Logs: `/var/log/printer-maintenance.log`
- Output: `/tmp/printer-output/printer-test.pdf`
- Cron config: `/etc/cron.d/printer-maintenance`

### On Host (with volumes)
- Logs: Docker volume `printer-logs`
- Output: Docker volume `printer-output`

## Notification Testing

Send test notification:
```bash
curl -d "Test notification" https://ntfy.sh/printer-maintenance
```

## Project Structure
```
Printer-Moisturiser/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration (73 lines)
│   ├── snmp_collector.py     # SNMP monitoring (145 lines)
│   ├── pdf_generator.py      # PDF generation (227 lines)
│   ├── ipp_printer.py        # IPP printing (113 lines)
│   ├── notification.py       # Notifications (117 lines)
│   └── main.py               # Entry point (153 lines)
├── Dockerfile                # Container definition (66 lines)
├── docker-compose.yaml       # Compose config (58 lines)
├── requirements.txt          # Dependencies (16 lines)
├── test.sh                   # Test script
├── .env.example              # Config template
├── README.md                 # Full documentation (246 lines)
├── CONTRIBUTING.md           # Contribution guide
└── .github/workflows/        # CI/CD
    └── build-and-test.yml    # GitHub Actions
```

Total: ~1,200 lines of code + documentation
