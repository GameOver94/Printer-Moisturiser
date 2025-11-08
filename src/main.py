"""Main entry point for the printer maintenance application.

This module orchestrates the printer maintenance workflow:
1. Gather printer information via SNMP
2. Generate PDF test page
3. Send to printer via IPP
4. Send notifications on success/failure
"""

import logging
import sys
from typing import Optional

from config import Config
from snmp_collector import SnmpCollector
from pdf_generator import PdfGenerator
from ipp_printer import IppPrinter
from notification import Notifier


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for the application.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    logger.info("=" * 60)
    logger.info("HP Smart Tank 7005 Printer Maintenance")
    logger.info("=" * 60)

    # Load configuration
    try:
        config = Config()
        if not config.validate():
            logger.error("Configuration validation failed")
            return 1
        
        logger.info("Configuration loaded successfully")
        logger.info(f"Printer IP: {config.get_printer_ip()}")
        logger.info(f"Printer Name: {config.get_printer_name()}")
        logger.info(f"Output Path: {config.get_output_path()}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1

    # Initialize notifier
    notifier: Optional[Notifier] = None
    try:
        notifier = Notifier(config.get_ntfy_channel())
        logger.info(f"Notifier initialized for channel: {config.get_ntfy_channel()}")
    except Exception as e:
        logger.error(f"Failed to initialize notifier: {e}")
        # Continue without notifications

    try:
        # Step 1: Collect printer information via SNMP
        logger.info("\n" + "=" * 60)
        logger.info("Step 1: Collecting printer information via SNMP")
        logger.info("=" * 60)
        
        snmpCollector = SnmpCollector(
            config.get_printer_ip(),
            config.get_snmp_community()
        )
        printerInfo = snmpCollector.collect_printer_info()
        
        logger.info("Printer information collected:")
        for key, value in printerInfo.items():
            if isinstance(value, dict):
                logger.info(f"  {key}:")
                for subKey, subValue in value.items():
                    logger.info(f"    {subKey}: {subValue}")
            else:
                logger.info(f"  {key}: {value}")

        # Step 2: Generate PDF test page
        logger.info("\n" + "=" * 60)
        logger.info("Step 2: Generating PDF test page")
        logger.info("=" * 60)
        
        pdfGenerator = PdfGenerator(config.get_output_path())
        pdfPath = pdfGenerator.generate_test_page(printerInfo)
        logger.info(f"PDF test page generated: {pdfPath}")

        # Step 3: Send to printer via IPP
        logger.info("\n" + "=" * 60)
        logger.info("Step 3: Sending test page to printer")
        logger.info("=" * 60)
        
        ippPrinter = IppPrinter(
            config.get_printer_ip(),
            config.get_printer_name()
        )
        
        printSuccess = ippPrinter.print_file(pdfPath)
        
        if printSuccess:
            logger.info("Test page sent to printer successfully")
            
            # Send success notification
            if notifier:
                notifier.send_success(
                    f"Printer maintenance completed successfully.\n\n"
                    f"Printer: {printerInfo.get('printer_name', 'Unknown')}\n"
                    f"Pages Printed: {printerInfo.get('pages_printed', 'Unknown')}\n"
                    f"Network Status: {printerInfo.get('network_status', 'Unknown')}"
                )
        else:
            logger.error("Failed to send test page to printer")
            
            # Send error notification
            if notifier:
                notifier.send_error(
                    f"Failed to send test page to printer.\n\n"
                    f"Printer IP: {config.get_printer_ip()}\n"
                    f"Network Status: {printerInfo.get('network_status', 'Unknown')}"
                )
            
            return 1

        logger.info("\n" + "=" * 60)
        logger.info("Printer maintenance completed successfully")
        logger.info("=" * 60)
        return 0

    except Exception as e:
        logger.error(f"Printer maintenance failed: {e}", exc_info=True)
        
        # Send error notification
        if notifier:
            notifier.send_error(
                f"Printer maintenance failed with exception.",
                error=e
            )
        
        return 1


if __name__ == "__main__":
    exitCode = main()
    sys.exit(exitCode)
