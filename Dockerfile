# Dockerfile for HP Smart Tank 7005 Printer Maintenance
# Optimized for ARM64 architecture (Raspberry Pi)

FROM python:3.14-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# - cups: For printing support
# - cups-client: CUPS client utilities
# - cron: For scheduling
# - snmp: For SNMP utilities (optional, for debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cups \
    cups-client \
    cron \
    snmp \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ /app/

# Create output directory for PDFs
RUN mkdir -p /tmp/printer-output && chmod 777 /tmp/printer-output

# Create printer setup script
RUN echo '#!/bin/bash\n\
# Setup printer in CUPS if printer configuration is provided\n\
if [ -n "$PRINTER_IP" ] && [ -n "$PRINTER_NAME" ]; then\n\
    echo "Setting up printer in CUPS..."\n\
    \n\
    # Start cupsd temporarily\n\
    cupsd\n\
    sleep 2\n\
    \n\
    # Get printer URI (default to IPP)\n\
    PRINTER_URI="${PRINTER_URI:-ipp://$PRINTER_IP/ipp/print}"\n\
    PRINTER_DRIVER="${PRINTER_DRIVER:-everywhere}"\n\
    \n\
    # Remove printer if it exists\n\
    lpadmin -x "$PRINTER_NAME" 2>/dev/null || true\n\
    \n\
    # Add the printer\n\
    echo "Adding printer: $PRINTER_NAME at $PRINTER_URI"\n\
    lpadmin -p "$PRINTER_NAME" -v "$PRINTER_URI" -E -m "$PRINTER_DRIVER"\n\
    \n\
    # Set as default if requested\n\
    if [ "$PRINTER_SET_DEFAULT" = "true" ]; then\n\
        lpadmin -d "$PRINTER_NAME"\n\
        echo "Set $PRINTER_NAME as default printer"\n\
    fi\n\
    \n\
    # Stop cupsd\n\
    pkill cupsd\n\
    sleep 1\n\
    \n\
    echo "Printer setup completed"\n\
else\n\
    echo "Skipping printer setup (PRINTER_IP or PRINTER_NAME not set)"\n\
fi\n\
' > /setup-printer.sh && chmod +x /setup-printer.sh

# Create startup script that runs cron and keeps container alive
RUN echo '#!/bin/bash\n\
echo "Starting Printer Maintenance Container..."\n\
\n\
# Setup printer in CUPS\n\
/setup-printer.sh\n\
\n\
# Start CUPS daemon\n\
echo "Starting CUPS daemon..."\n\
cupsd\n\
sleep 2\n\
\n\
# Get cron schedule from environment variable or use default\n\
CRON_SCHEDULE="${CRON_SCHEDULE:-0 2 * * 0}"\n\
echo "Cron schedule: $CRON_SCHEDULE"\n\
echo ""\n\
# Create cron job with the configured schedule\n\
echo "$CRON_SCHEDULE cd /app && /usr/local/bin/python main.py >> /var/log/printer-maintenance.log 2>&1" > /etc/cron.d/printer-maintenance\n\
chmod 0644 /etc/cron.d/printer-maintenance\n\
crontab /etc/cron.d/printer-maintenance\n\
touch /var/log/printer-maintenance.log\n\
# Run once at startup\n\
echo "Running initial printer maintenance..."\n\
cd /app && /usr/local/bin/python main.py\n\
echo ""\n\
# Start cron in foreground\n\
echo "Starting cron scheduler..."\n\
cron && tail -f /var/log/printer-maintenance.log\n\
' > /start.sh && chmod +x /start.sh

# Expose volumes for logs and output
VOLUME ["/var/log", "/tmp/printer-output"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep cron || exit 1

# Run startup script
CMD ["/start.sh"]
