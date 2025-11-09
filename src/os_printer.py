"""Operating system printing helpers.

Wraps platform-native printing APIs so PDFs can be handed off to the spooler
instead of relying on direct IPP calls.
"""

from __future__ import annotations

import logging
import os
import platform
from dataclasses import dataclass
from typing import Optional


logger = logging.getLogger(__name__)


class PrinterError(RuntimeError):
    """Raised when the OS printing layer is unavailable."""


@dataclass
class PrintJobConfig:
    """Configuration for a single print job."""

    printer_name: Optional[str]
    job_title: str
    duplex: bool


class OsPrinter:
    """Delegate document printing to the host operating system."""

    def __init__(self, printer_name: Optional[str], duplex: bool) -> None:
        self.m_job_config = PrintJobConfig(
            printer_name=printer_name,
            job_title="Printer Maintenance Test Page",
            duplex=duplex,
        )

    def print_file(self, file_path: str) -> bool:
        """Print the given file via the OS spooler."""

        if not os.path.exists(file_path):
            logger.error("Print file not found: %s", file_path)
            return False

        system = platform.system()
        logger.info("Delegating print job to %s subsystem", system or "Unknown")

        try:
            if system in {"Linux", "Darwin"}:
                self._print_cups(file_path)
            else:
                raise PrinterError(f"Unsupported operating system: {system}")
        except PrinterError as exc:
            logger.error("Unable to submit print job: %s", exc)
            return False
        except Exception as exc:  # pragma: no cover - platform specific failures
            logger.error("Unexpected print failure: %s", exc, exc_info=True)
            return False

        logger.info("Print job handed off to operating system")
        return True


    def _print_cups(self, file_path: str) -> None:
        """Submit a print job via CUPS (Linux/macOS)."""

        try:
            import cups  # type: ignore[import]
        except ImportError as exc:  # pragma: no cover - only hit when dependency missing
            raise PrinterError("pycups is required for CUPS printing") from exc

        connection = cups.Connection()
        printers = connection.getPrinters()
        printer_name = self.m_job_config.printer_name or connection.getDefault()

        if not printer_name:
            raise PrinterError("No printer specified and no system default set")
        if printer_name not in printers:
            raise PrinterError(f"Printer '{printer_name}' not found in CUPS")

        logger.info("Submitting CUPS job to printer %s", printer_name)
        options = {}
        if self.m_job_config.duplex:
            options["sides"] = "two-sided-long-edge"

        job_id = connection.printFile(printer_name, file_path, self.m_job_config.job_title, options)
        logger.debug("CUPS job id: %s", job_id)

