"""PDF generator module for creating test pages.

This module generates PDF test pages with printer information and test patterns.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from reportlab.lib.colors import black, blue, cyan, green, magenta, red, yellow
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


logger = logging.getLogger(__name__)


class PdfGenerator:
    """PDF generator for creating printer test pages."""

    def __init__(self, outputPath: str) -> None:
        """Initialize PDF generator.

        Args:
            outputPath: Path where the PDF will be saved.
        """
        self.m_outputPath: Path = Path(outputPath).expanduser()

    def _draw_printer_info(self, canvasObj: canvas.Canvas, printerInfo: Dict[str, Any], startY: float) -> float:
        """Draw printer information on the PDF.

        Args:
            canvasObj: The canvas object to draw on.
            printerInfo: Dictionary containing printer information.
            startY: Starting Y position.

        Returns:
            float: Updated Y position after drawing.
        """
        canvasObj.setFont("Helvetica-Bold", 16)
        canvasObj.drawString(inch, startY, "HP Smart Tank 7005 - Printer Information")
        currentY = startY - 30

        canvasObj.setFont("Helvetica", 10)
        
        # Basic information
        infoLines = [
            f"Model Name: {printerInfo.get('model_name', 'Unknown')}",
            f"Model Number: {printerInfo.get('device_description', 'Unknown')}",
            f"Printer Name: {printerInfo.get('printer_name', 'Unknown')}",
            f"Serial Number: {printerInfo.get('serial_number', 'Unknown')}",
            f"Pages Printed: {printerInfo.get('pages_printed', 'Unknown')}",
            f"IP Address: {printerInfo.get('ip_address', 'Unknown')}",
            f"Network Status: {printerInfo.get('network_status', 'Unknown')}",
            f"Uptime: {printerInfo.get('uptime', 'Unknown')}",
        ]

        for line in infoLines:
            canvasObj.drawString(inch, currentY, line)
            currentY -= 15

        # Ink levels
        inkLevels = printerInfo.get('ink_levels', {})
        canvasObj.drawString(inch, currentY, "Estimated Tank Levels:")
        currentY -= 15
        canvasObj.drawString(inch + 20, currentY, f"  Cyan: {inkLevels.get('cyan', 'Unknown')}")
        currentY -= 15
        canvasObj.drawString(inch + 20, currentY, f"  Magenta: {inkLevels.get('magenta', 'Unknown')}")
        currentY -= 15
        canvasObj.drawString(inch + 20, currentY, f"  Yellow: {inkLevels.get('yellow', 'Unknown')}")
        currentY -= 15
        canvasObj.drawString(inch + 20, currentY, f"  Black: {inkLevels.get('black', 'Unknown')}")
        currentY -= 30

        return currentY

    def _draw_line_test_patterns(self, canvasObj: canvas.Canvas, startY: float) -> float:
        """Draw line test patterns on the PDF.

        Args:
            canvasObj: The canvas object to draw on.
            startY: Starting Y position.

        Returns:
            float: Updated Y position after drawing.
        """
        canvasObj.setFont("Helvetica-Bold", 12)
        canvasObj.drawString(inch, startY, "Line Test Patterns")
        currentY = startY - 20

        # Horizontal lines with varying thickness
        lineWidths = [0.5, 1, 1.5, 2, 3]
        for width in lineWidths:
            canvasObj.setLineWidth(width)
            canvasObj.line(inch, currentY, 7.5 * inch, currentY)
            canvasObj.setFont("Helvetica", 8)
            canvasObj.drawString(inch, currentY - 10, f"{width}pt line")
            currentY -= 20

        currentY -= 10

        # Vertical lines
        canvasObj.setFont("Helvetica-Bold", 10)
        canvasObj.drawString(inch, currentY, "Vertical Lines:")
        currentY -= 15
        
        xPos = inch + 20
        for width in [0.5, 1, 1.5, 2, 3]:
            canvasObj.setLineWidth(width)
            canvasObj.line(xPos, currentY, xPos, currentY - 50)
            xPos += 40

        currentY -= 60

        # Grid pattern
        canvasObj.setFont("Helvetica-Bold", 10)
        canvasObj.drawString(inch, currentY, "Grid Pattern:")
        currentY -= 15

        canvasObj.setLineWidth(0.5)
        gridSize = 20
        for i in range(10):
            x = inch + (i * gridSize)
            canvasObj.line(x, currentY, x, currentY - (10 * gridSize))
        for i in range(11):
            y = currentY - (i * gridSize)
            canvasObj.line(inch, y, inch + (10 * gridSize), y)

        currentY -= (10 * gridSize) - 20

        return currentY

    def _draw_color_blocks(self, canvasObj: canvas.Canvas, startY: float) -> float:
        """Draw large color blocks for print quality testing.

        Args:
            canvasObj: The canvas object to draw on.
            startY: Starting Y position.

        Returns:
            float: Updated Y position after drawing.
        """
        canvasObj.setFont("Helvetica-Bold", 12)
        canvasObj.drawString(inch, startY, "Color Block Test Patterns")
        currentY = startY - 30

        # Define colors and their names
        colors = [
            (cyan, "Cyan"),
            (magenta, "Magenta"),
            (yellow, "Yellow"),
            (black, "Black"),
            (red, "Red"),
            (green, "Green"),
            (blue, "Blue"),
        ]

        blockWidth = 1.5 * inch
        blockHeight = 0.75 * inch
        xPos = inch
        yPos = currentY

        for color, colorName in colors:
            # Draw color block
            canvasObj.setFillColor(color)
            canvasObj.rect(xPos, yPos - blockHeight, blockWidth, blockHeight, fill=1, stroke=0)
            
            # Draw label
            canvasObj.setFillColor(black)
            canvasObj.setFont("Helvetica", 8)
            canvasObj.drawString(xPos, yPos - blockHeight - 12, colorName)

            xPos += blockWidth + 20
            if xPos > 6.5 * inch:
                xPos = inch
                yPos -= blockHeight + 30

        currentY = yPos - blockHeight - 30

        return currentY

    def generate_test_page(self, printerInfo: Dict[str, Any]) -> str:
        """Generate a PDF test page with printer information and test patterns.

        Args:
            printerInfo: Dictionary containing printer information.

        Returns:
            str: Path to the generated PDF file.

        Raises:
            Exception: If PDF generation fails.
        """
        logger.info(f"Generating PDF test page: {self.m_outputPath}")

        try:
            self.m_outputPath.parent.mkdir(parents=True, exist_ok=True)

            canvasObj = canvas.Canvas(str(self.m_outputPath), pagesize=letter)
            pageWidth, pageHeight = letter

            # Start from top of page
            currentY = pageHeight - inch

            # Draw printer information
            currentY = self._draw_printer_info(canvasObj, printerInfo, currentY)

            # Draw line test patterns
            if currentY < 3 * inch:
                canvasObj.showPage()
                currentY = pageHeight - inch

            currentY = self._draw_line_test_patterns(canvasObj, currentY)

            # Draw color blocks
            if currentY < 4 * inch:
                canvasObj.showPage()
                currentY = pageHeight - inch

            currentY = self._draw_color_blocks(canvasObj, currentY)

            # Save the PDF
            canvasObj.save()

            logger.info(f"PDF test page generated successfully: {self.m_outputPath}")
            return str(self.m_outputPath)

        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise Exception(f"PDF generation failed: {e}")
