# Dockerfile for HP Smart Tank 7005 Printer Maintenance
# Optimized for ARM64 architecture (Raspberry Pi)

FROM python:3.14-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# - cups: For IPP printing support
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

# Create cron job for weekly execution
# Run every Sunday at 2:00 AM
RUN echo "0 2 * * 0 cd /app && /usr/local/bin/python main.py >> /var/log/printer-maintenance.log 2>&1" > /etc/cron.d/printer-maintenance && \
    chmod 0644 /etc/cron.d/printer-maintenance && \
    crontab /etc/cron.d/printer-maintenance && \
    touch /var/log/printer-maintenance.log

# Create startup script that runs cron and keeps container alive
RUN echo '#!/bin/bash\n\
echo "Starting Printer Maintenance Container..."\n\
echo "Cron schedule: Weekly (Sunday at 2:00 AM)"\n\
echo ""\n\
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
