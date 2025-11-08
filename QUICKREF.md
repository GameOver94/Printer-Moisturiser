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

#### Linux/Mac
```bash
# Run test script
./test.sh

# Test imports only
cd src && python3 -c "from config import Config; from snmp_collector import SnmpCollector; from pdf_generator import PdfGenerator; from ipp_printer import IppPrinter; from notification import Notifier"

# Run main application
cd src && python3 main.py
```

#### Windows
```powershell
# Run test script (activates .venv automatically)
.\test.ps1

# Run main application
cd src
python main.py
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
export CRON_SCHEDULE="0 2 * * 0"
```

## Cron Schedule Examples

Set via `CRON_SCHEDULE` environment variable (no need to edit Dockerfile):

```bash
# In .env file or docker-compose.yaml
CRON_SCHEDULE="0 3 * * *"    # Daily at 3:00 AM
CRON_SCHEDULE="0 9 * * 1"    # Every Monday at 9:00 AM
CRON_SCHEDULE="0 2 * * 1,4"  # Monday & Thursday at 2:00 AM
CRON_SCHEDULE="0 */6 * * *"  # Every 6 hours
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
# The application uses pyipp library (pure Python)
# No manual testing command needed - check application logs for IPP communication
docker-compose logs -f
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
│   ├── ipp_printer.py        # IPP printing with pyipp (155 lines)
│   ├── notification.py       # Notifications (117 lines)
│   └── main.py               # Entry point (153 lines)
├── Dockerfile                # Container definition (60 lines)
├── docker-compose.yaml       # Compose config (61 lines)
├── requirements.txt          # Dependencies (17 lines)
├── test.sh                   # Test script (Bash)
├── test.ps1                  # Test script (PowerShell)
├── .env.example              # Config template
├── README.md                 # Full documentation
├── CONTRIBUTING.md           # Contribution guide
├── QUICKREF.md               # Quick reference
└── .github/workflows/        # CI/CD
    └── build-and-test.yml    # GitHub Actions
```

Total: ~1,300 lines of code + documentation
