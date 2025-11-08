"""IPP printer module for sending documents to the printer.

This module handles printing via the Internet Printing Protocol (IPP).
"""

import logging
from typing import Optional
import subprocess
import os


logger = logging.getLogger(__name__)


class IppPrinter:
    """IPP printer client for sending documents to the printer."""

    def __init__(self, printerIp: str, printerName: str) -> None:
        """Initialize IPP printer.

        Args:
            printerIp: IP address of the printer.
            printerName: Name of the printer.
        """
        self.m_printerIp: str = printerIp
        self.m_printerName: str = printerName
        self.m_printerUri: str = f"ipp://{printerIp}/ipp/print"

    def print_file(self, filePath: str) -> bool:
        """Print a file to the printer using IPP.

        Args:
            filePath: Path to the file to print.

        Returns:
            bool: True if printing succeeded, False otherwise.
        """
        if not os.path.exists(filePath):
            logger.error(f"File not found: {filePath}")
            return False

        logger.info(f"Printing {filePath} to {self.m_printerUri}")

        try:
            # Use lp command with IPP URI
            # The lp command is part of CUPS and supports IPP directly
            cmd = [
                "lp",
                "-d", self.m_printerUri,
                "-t", f"{self.m_printerName} Test Page",
                "-o", "fit-to-page",
                filePath
            ]

            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Print job submitted successfully: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"Print job failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Print job timed out after 30 seconds")
            return False
        except FileNotFoundError:
            logger.error("lp command not found. CUPS may not be installed.")
            return False
        except Exception as e:
            logger.error(f"Failed to print file: {e}")
            return False

    def check_printer_status(self) -> bool:
        """Check if the printer is reachable via IPP.

        Returns:
            bool: True if printer is reachable, False otherwise.
        """
        try:
            # Try to query printer status using lpstat
            cmd = ["lpstat", "-h", self.m_printerIp, "-p"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Printer is reachable via IPP")
                return True
            else:
                logger.warning(f"Printer status check returned: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Printer status check timed out")
            return False
        except FileNotFoundError:
            logger.warning("lpstat command not found. Skipping printer status check.")
            return True  # Assume printer is available if we can't check
        except Exception as e:
            logger.error(f"Failed to check printer status: {e}")
            return False
