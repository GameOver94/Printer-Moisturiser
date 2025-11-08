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

- **IPP Printing**: Sends test pages directly to the printer via Internet Printing Protocol using pure Python (pyipp library, no CUPS dependency)

- **Error Notifications**: Sends alerts to ntfy.sh on failures or completion

- **Docker Support**: Optimized for ARM64 architecture (Raspberry Pi)

- **Automated Scheduling**: Configurable cron job via environment variable (default: Sunday at 2:00 AM)

- **Cross-Platform Testing**: Includes both Bash and PowerShell test scripts

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

# Optional: Cron schedule (default: 0 2 * * 0 - Sunday at 2:00 AM)
CRON_SCHEDULE=0 2 * * 0
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
| `CRON_SCHEDULE` | No | `0 2 * * 0` | Cron schedule (Sunday at 2:00 AM) |

### Customizing the Schedule

You can now customize the maintenance schedule via the `CRON_SCHEDULE` environment variable without rebuilding the Docker image:

```env
# In .env file
CRON_SCHEDULE=0 3 * * *  # Daily at 3:00 AM
CRON_SCHEDULE=0 9 * * 1  # Every Monday at 9:00 AM
CRON_SCHEDULE=0 2 * * 0  # Every Sunday at 2:00 AM (default)
```

Cron format: `minute hour day month weekday`

Examples:
- Daily at 3 AM: `0 3 * * *`
- Every Monday at 9 AM: `0 9 * * 1`
- Twice weekly (Mon & Thu at 2 AM): `0 2 * * 1,4`

Changes take effect on next container restart:
```bash
docker-compose up -d
```

## Local Testing

The project includes test scripts for both Linux/Mac and Windows:

### Linux/Mac (Bash)
```bash
./test.sh
```

### Windows (PowerShell)
```powershell
.\test.ps1
```

The PowerShell script will:
1. Check for and create a virtual environment at `.venv` if it doesn't exist
2. Activate the virtual environment
3. Install dependencies
4. Run the application with test configuration

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
2. Check printer connectivity:
   ```bash
   docker exec hp-printer-maintenance ping -c 4 <PRINTER_IP>
   ```

3. Test IPP connection with pyipp (the application will log detailed errors)

### Container Won't Start

1. Check logs:
   ```bash
   docker-compose logs
   ```

2. Verify environment variables are set correctly

3. Ensure no port conflicts if not using host networking

## Development

### Running Locally (Without Docker)

#### Linux/Mac

1. Install Python 3.12 or higher

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
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

Or simply use the test script:
```bash
./test.sh
```

#### Windows

1. Install Python 3.12 or higher

2. Create and activate virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```powershell
   $env:PRINTER_IP="192.168.1.100"
   $env:NTFY_CHANNEL="printer-maintenance"
   ```

5. Run the application:
   ```powershell
   cd src
   python main.py
   ```

Or simply use the test script:
```powershell
.\test.ps1
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
