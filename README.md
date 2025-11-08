# Printer Moisturiser

A complete Python 3.14 application for HP Smart Tank 7005 printer maintenance that automatically generates and prints test pages to keep the print heads from drying out.

## Features

- **SNMP Monitoring**: Gathers comprehensive printer information including:
  - Model Name and Model Number
  - Printer Name and Serial Number
  - Total Pages Printed
  - Estimated Ink Tank Levels (Cyan, Magenta, Yellow, Black)
  - Network Status and IP Address
  - System Uptime

- **PDF Test Page Generation**: Creates detailed test pages with:
  - Printer information summary
  - Line test patterns (various thicknesses and orientations)
  - Grid patterns for alignment testing
  - Large color blocks for print quality assessment

- **IPP Printing**: Sends test pages directly to the printer via Internet Printing Protocol

- **Error Notifications**: Sends alerts to ntfy.sh on failures or completion

- **Docker Support**: Optimized for ARM64 architecture (Raspberry Pi)

- **Automated Scheduling**: Weekly cron job (Sunday at 2:00 AM by default)

## Requirements

- Docker and Docker Compose
- Raspberry Pi (ARM64) or compatible system
- HP Smart Tank 7005 printer on the same network
- Printer with SNMP enabled

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/GameOver94/Printer-Moisturiser.git
cd Printer-Moisturiser
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required: Your printer's IP address
PRINTER_IP=192.168.1.100

# Required: Your ntfy.sh channel for notifications
NTFY_CHANNEL=printer-maintenance

# Optional: Printer name for display
PRINTER_NAME=HP Smart Tank 7005

# Optional: SNMP community string (default: public)
SNMP_COMMUNITY=public

# Optional: Output path for PDFs
OUTPUT_PATH=/tmp/printer-output/printer-test.pdf

# Optional: Timezone
TZ=America/New_York
```

### 3. Build and Run with Docker Compose

```bash
docker-compose up -d
```

The container will:
1. Run an initial printer maintenance task immediately
2. Start the cron scheduler for weekly execution
3. Continue running in the background

### 4. View Logs

```bash
# View real-time logs
docker-compose logs -f

# View cron job logs
docker exec hp-printer-maintenance tail -f /var/log/printer-maintenance.log
```

## Manual Execution

To run the maintenance task manually:

```bash
docker exec hp-printer-maintenance /usr/local/bin/python /app/main.py
```

## Project Structure

```
Printer-Moisturiser/
├── src/
│   ├── main.py              # Main entry point with workflow orchestration
│   ├── config.py            # Configuration management
│   ├── snmp_collector.py    # SNMP printer information collection
│   ├── pdf_generator.py     # PDF test page generation
│   ├── ipp_printer.py       # IPP printing support
│   └── notification.py      # ntfy.sh notification handling
├── Dockerfile               # Docker image definition (ARM64 optimized)
├── docker-compose.yaml      # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PRINTER_IP` | Yes | `192.168.1.100` | IP address of the printer |
| `NTFY_CHANNEL` | Yes | `printer-maintenance` | ntfy.sh channel for notifications |
| `PRINTER_NAME` | No | `HP Smart Tank 7005` | Printer name for display |
| `SNMP_COMMUNITY` | No | `public` | SNMP community string |
| `OUTPUT_PATH` | No | `/tmp/printer-output/printer-test.pdf` | Output path for generated PDFs |
| `TZ` | No | `UTC` | Timezone for cron scheduling |

### Customizing the Schedule

To change the cron schedule, edit the Dockerfile:

```dockerfile
# Default: Every Sunday at 2:00 AM
RUN echo "0 2 * * 0 cd /app && /usr/local/bin/python main.py >> /var/log/printer-maintenance.log 2>&1" > /etc/cron.d/printer-maintenance
```

Cron format: `minute hour day month weekday`

Examples:
- Daily at 3 AM: `0 3 * * *`
- Every Monday at 9 AM: `0 9 * * 1`
- Twice weekly (Mon & Thu at 2 AM): `0 2 * * 1,4`

After modifying, rebuild the container:
```bash
docker-compose up -d --build
```

## Notifications

The application sends notifications to [ntfy.sh](https://ntfy.sh) for:
- ✅ **Success**: When maintenance completes successfully
- ⚠️ **Errors**: When any step fails

To receive notifications:
1. Install the ntfy app on your phone (iOS/Android) or use the web interface
2. Subscribe to your configured channel (e.g., `printer-maintenance`)

## Troubleshooting

### Printer Not Responding

1. Check network connectivity:
   ```bash
   docker exec hp-printer-maintenance ping -c 4 <PRINTER_IP>
   ```

2. Verify SNMP is enabled on the printer:
   ```bash
   docker exec hp-printer-maintenance snmpwalk -v2c -c public <PRINTER_IP> system
   ```

3. Check printer web interface (usually `http://<PRINTER_IP>`)

### Print Job Fails

1. Verify IPP is enabled on the printer
2. Check CUPS status in container:
   ```bash
   docker exec hp-printer-maintenance lpstat -h <PRINTER_IP> -p
   ```

3. Try printing manually:
   ```bash
   docker exec hp-printer-maintenance lp -d ipp://<PRINTER_IP>/ipp/print /tmp/printer-output/printer-test.pdf
   ```

### Container Won't Start

1. Check logs:
   ```bash
   docker-compose logs
   ```

2. Verify environment variables are set correctly

3. Ensure no port conflicts if not using host networking

## Development

### Running Locally (Without Docker)

1. Install Python 3.14

2. Install system dependencies:
   ```bash
   sudo apt-get install cups cups-client snmp
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```bash
   export PRINTER_IP=192.168.1.100
   export NTFY_CHANNEL=printer-maintenance
   ```

5. Run the application:
   ```bash
   cd src
   python main.py
   ```

### Code Style

The codebase follows these conventions:
- Functions: `snake_case`
- Variables: `camelCase`
- Private members: `m_` prefix
- Full type hinting throughout
- Comprehensive docstrings

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/GameOver94/Printer-Moisturiser/issues) page.
