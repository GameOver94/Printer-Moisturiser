"""IPP printer module for sending documents to the printer.

This module handles printing via the Internet Printing Protocol (IPP).
"""

import logging
from typing import Optional
import asyncio
from pyipp import IPP, Printer as IppPrinterClient
from pyipp.enums import IppOperation
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

    async def _async_print_file(self, filePath: str) -> bool:
        """Asynchronously print a file to the printer using IPP.

        Args:
            filePath: Path to the file to print.

        Returns:
            bool: True if printing succeeded, False otherwise.
        """
        try:
            # Create IPP client
            ipp = IPP(host=self.m_printerIp)
            
            # Get printer information first
            printer: IppPrinterClient = await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "printer-uri": self.m_printerUri,
                    "requested-attributes": [
                        "printer-name",
                        "printer-state",
                        "printer-state-message",
                    ],
                },
            )
            
            logger.info(f"Printer state: {printer.info.state}")
            logger.info(f"Printer name: {printer.info.name}")
            
            # Read the PDF file
            with open(filePath, "rb") as f:
                documentData = f.read()
            
            # Submit print job
            result = await ipp.execute(
                IppOperation.PRINT_JOB,
                {
                    "printer-uri": self.m_printerUri,
                    "requesting-user-name": "printer-maintenance",
                    "job-name": f"{self.m_printerName} Test Page",
                    "document-format": "application/pdf",
                    "document": documentData,
                },
            )
            
            logger.info(f"Print job submitted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to print file via IPP: {e}")
            return False

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
            # Run the async print function
            return asyncio.run(self._async_print_file(filePath))
        except Exception as e:
            logger.error(f"Failed to print file: {e}")
            return False

    async def _async_check_printer_status(self) -> bool:
        """Asynchronously check if the printer is reachable via IPP.

        Returns:
            bool: True if printer is reachable, False otherwise.
        """
        try:
            # Create IPP client
            ipp = IPP(host=self.m_printerIp)
            
            # Get printer information
            printer: IppPrinterClient = await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "printer-uri": self.m_printerUri,
                    "requested-attributes": [
                        "printer-name",
                        "printer-state",
                        "printer-state-message",
                    ],
                },
            )
            
            logger.info(f"Printer is reachable via IPP")
            logger.info(f"Printer state: {printer.info.state}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check printer status: {e}")
            return False

    def check_printer_status(self) -> bool:
        """Check if the printer is reachable via IPP.

        Returns:
            bool: True if printer is reachable, False otherwise.
        """
        try:
            # Run the async status check
            return asyncio.run(self._async_check_printer_status())
        except Exception as e:
            logger.error(f"Failed to check printer status: {e}")
            return False
