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
cd src && python3 -c "from config import Config; from snmp_collector import SnmpCollector; from pdf_generator import PdfGenerator; from os_printer import OsPrinter; from notification import Notifier"

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

# CUPS Configuration (Optional)
export PRINTER_URI="ipp://192.168.1.100/ipp/print"
export PRINTER_DRIVER="everywhere"
export PRINTER_SET_DEFAULT="true"
export PRINT_DUPLEX="false"
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

### Test CUPS printing
```bash
# Check CUPS status
docker exec hp-printer-maintenance lpstat -t

# List printers
docker exec hp-printer-maintenance lpstat -p -d

# Check print queue
docker exec hp-printer-maintenance lpstat -o

# View CUPS logs
docker exec hp-printer-maintenance tail -f /var/log/cups/error_log

# Test print manually
docker exec hp-printer-maintenance lp -d "HP Smart Tank 7005" /tmp/test.pdf
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
- CUPS logs: `/var/log/cups/`
- Output: `/tmp/printer-output/printer-test.pdf`
- Cron config: `/etc/cron.d/printer-maintenance`
- Printer setup: `/setup-printer.sh`

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
│   ├── config.py             # Configuration
│   ├── snmp_collector.py     # SNMP monitoring
│   ├── pdf_generator.py      # PDF generation
│   ├── os_printer.py         # OS printing (CUPS)
│   ├── notification.py       # Notifications
│   └── main.py               # Entry point
├── Dockerfile                # Container definition with CUPS
├── docker-compose.yaml       # Compose config (bridge network)
├── requirements.txt          # Dependencies (with pycups)
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
