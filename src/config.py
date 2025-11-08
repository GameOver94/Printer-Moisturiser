"""Configuration module for printer maintenance application.

This module handles all environment variable configuration for the application.
"""

import os
from typing import Optional


class Config:
    """Configuration class that loads settings from environment variables."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.m_printerIp: str = os.getenv("PRINTER_IP", "192.168.1.100")
        self.m_ntfyChannel: str = os.getenv("NTFY_CHANNEL", "printer-maintenance")
        self.m_printerName: str = os.getenv("PRINTER_NAME", "HP Smart Tank 7005")
        self.m_snmpCommunity: str = os.getenv("SNMP_COMMUNITY", "public")
        self.m_outputPath: str = os.getenv("OUTPUT_PATH", "/tmp/printer-test.pdf")

    def get_printer_ip(self) -> str:
        """Get the printer IP address.

        Returns:
            str: The configured printer IP address.
        """
        return self.m_printerIp

    def get_ntfy_channel(self) -> str:
        """Get the ntfy.sh channel name.

        Returns:
            str: The configured ntfy.sh channel.
        """
        return self.m_ntfyChannel

    def get_printer_name(self) -> str:
        """Get the printer name.

        Returns:
            str: The configured printer name.
        """
        return self.m_printerName

    def get_snmp_community(self) -> str:
        """Get the SNMP community string.

        Returns:
            str: The configured SNMP community string.
        """
        return self.m_snmpCommunity

    def get_output_path(self) -> str:
        """Get the output path for generated PDFs.

        Returns:
            str: The configured output path.
        """
        return self.m_outputPath

    def validate(self) -> bool:
        """Validate that all required configuration is present.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not self.m_printerIp:
            return False
        if not self.m_ntfyChannel:
            return False
        if not self.m_outputPath:
            return False
        return True
