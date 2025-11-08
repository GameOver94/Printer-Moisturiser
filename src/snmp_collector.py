"""SNMP collector module for gathering printer information.

This module collects printer information via SNMP protocol.
"""

from typing import Dict, Optional, Any
from pysnmp.hlapi import (
    getCmd,
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
)
import logging


logger = logging.getLogger(__name__)


class SnmpCollector:
    """SNMP collector for gathering printer information."""

    # Standard Printer MIB OIDs
    OID_MODEL_NAME = "1.3.6.1.2.1.25.3.2.1.3.1"
    OID_SERIAL_NUMBER = "1.3.6.1.2.1.43.5.1.1.17.1"
    OID_DEVICE_DESC = "1.3.6.1.2.1.25.3.2.1.3.1"
    OID_TOTAL_PAGES = "1.3.6.1.2.1.43.10.2.1.4.1.1"
    OID_SYS_NAME = "1.3.6.1.2.1.1.5.0"
    OID_SYS_UPTIME = "1.3.6.1.2.1.1.3.0"
    OID_SYS_DESCR = "1.3.6.1.2.1.1.1.0"

    # HP-specific OIDs for ink levels
    OID_CYAN_LEVEL = "1.3.6.1.2.1.43.11.1.1.9.1.1"
    OID_MAGENTA_LEVEL = "1.3.6.1.2.1.43.11.1.1.9.1.2"
    OID_YELLOW_LEVEL = "1.3.6.1.2.1.43.11.1.1.9.1.3"
    OID_BLACK_LEVEL = "1.3.6.1.2.1.43.11.1.1.9.1.4"

    def __init__(self, printerIp: str, community: str = "public") -> None:
        """Initialize SNMP collector.

        Args:
            printerIp: IP address of the printer.
            community: SNMP community string (default: "public").
        """
        self.m_printerIp: str = printerIp
        self.m_community: str = community
        self.m_snmpEngine = SnmpEngine()
        self.m_communityData = CommunityData(self.m_community)
        self.m_transportTarget = UdpTransportTarget((self.m_printerIp, 161), timeout=5, retries=3)
        self.m_contextData = ContextData()

    def _snmp_get(self, oid: str) -> Optional[str]:
        """Perform SNMP GET operation.

        Args:
            oid: The OID to query.

        Returns:
            Optional[str]: The value from SNMP query, or None if query fails.
        """
        try:
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(
                    self.m_snmpEngine,
                    self.m_communityData,
                    self.m_transportTarget,
                    self.m_contextData,
                    ObjectType(ObjectIdentity(oid)),
                )
            )

            if errorIndication:
                logger.warning(f"SNMP error indication: {errorIndication}")
                return None
            elif errorStatus:
                logger.warning(
                    f"SNMP error status: {errorStatus.prettyPrint()} at {errorIndex}"
                )
                return None
            else:
                for varBind in varBinds:
                    return str(varBind[1])
        except Exception as e:
            logger.error(f"SNMP query failed for OID {oid}: {e}")
            return None

        return None

    def collect_printer_info(self) -> Dict[str, Any]:
        """Collect all printer information via SNMP.

        Returns:
            Dict[str, Any]: Dictionary containing printer information.
        """
        printerInfo: Dict[str, Any] = {}

        logger.info(f"Collecting SNMP data from {self.m_printerIp}")

        # Basic printer information
        printerInfo["model_name"] = self._snmp_get(self.OID_MODEL_NAME) or "Unknown"
        printerInfo["serial_number"] = self._snmp_get(self.OID_SERIAL_NUMBER) or "Unknown"
        printerInfo["printer_name"] = self._snmp_get(self.OID_SYS_NAME) or "Unknown"
        printerInfo["system_description"] = self._snmp_get(self.OID_SYS_DESCR) or "Unknown"
        printerInfo["device_description"] = self._snmp_get(self.OID_DEVICE_DESC) or "Unknown"

        # Pages printed
        totalPages = self._snmp_get(self.OID_TOTAL_PAGES)
        printerInfo["pages_printed"] = totalPages or "Unknown"

        # Uptime
        uptime = self._snmp_get(self.OID_SYS_UPTIME)
        if uptime:
            try:
                uptimeTicks = int(uptime)
                uptimeSeconds = uptimeTicks // 100
                uptimeDays = uptimeSeconds // 86400
                uptimeHours = (uptimeSeconds % 86400) // 3600
                uptimeMinutes = (uptimeSeconds % 3600) // 60
                printerInfo["uptime"] = f"{uptimeDays}d {uptimeHours}h {uptimeMinutes}m"
            except ValueError:
                printerInfo["uptime"] = uptime
        else:
            printerInfo["uptime"] = "Unknown"

        # Ink levels
        cyanLevel = self._snmp_get(self.OID_CYAN_LEVEL)
        magentaLevel = self._snmp_get(self.OID_MAGENTA_LEVEL)
        yellowLevel = self._snmp_get(self.OID_YELLOW_LEVEL)
        blackLevel = self._snmp_get(self.OID_BLACK_LEVEL)

        printerInfo["ink_levels"] = {
            "cyan": cyanLevel or "Unknown",
            "magenta": magentaLevel or "Unknown",
            "yellow": yellowLevel or "Unknown",
            "black": blackLevel or "Unknown",
        }

        # Network information
        printerInfo["ip_address"] = self.m_printerIp
        printerInfo["network_status"] = "Connected" if printerInfo["model_name"] != "Unknown" else "Disconnected"

        logger.info("SNMP data collection completed")
        return printerInfo
