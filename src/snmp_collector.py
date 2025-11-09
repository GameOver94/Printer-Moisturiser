"""SNMP collector module for gathering printer information using PySNMP v7."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)


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
        self.m_timeout: float = 5
        self.m_retries: int = 3
        self.m_contextData = ContextData()

    async def _create_transport(self) -> UdpTransportTarget:
        """Create a UDP transport target for SNMP queries."""

        return await UdpTransportTarget.create(
            (self.m_printerIp, 161), timeout=self.m_timeout, retries=self.m_retries
        )

    async def _snmp_get_async(
        self, transport: UdpTransportTarget, oid: str
    ) -> Optional[str]:
        """Perform a single SNMP GET using the asyncio PySNMP API."""

        try:
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                self.m_snmpEngine,
                self.m_communityData,
                transport,
                self.m_contextData,
                ObjectType(ObjectIdentity(oid)),
            )
        except Exception as exc:  # pragma: no cover - network errors are runtime dependent
            logger.error(f"SNMP query failed for OID {oid}: {exc}")
            return None

        if errorIndication:
            logger.warning(f"SNMP error indication: {errorIndication}")
            return None

        if errorStatus:
            status_method = getattr(errorStatus, "prettyPrint", None)
            status_text = status_method() if callable(status_method) else str(errorStatus)
            logger.warning(
                f"SNMP error status: {status_text} at index {errorIndex}"
            )
            return None

        for varBind in varBinds:
            return str(varBind[1])

        return None

    async def _collect_printer_info_async(self) -> Dict[str, Any]:
        """Collect printer information asynchronously using a shared transport."""

        transport = await self._create_transport()
        try:
            printerInfo: Dict[str, Any] = {}

            # Basic printer information
            printerInfo["model_name"] = await self._snmp_get_async(
                transport, self.OID_MODEL_NAME
            ) or "Unknown"
            printerInfo["serial_number"] = await self._snmp_get_async(
                transport, self.OID_SERIAL_NUMBER
            ) or "Unknown"
            printerInfo["printer_name"] = await self._snmp_get_async(
                transport, self.OID_SYS_NAME
            ) or "Unknown"
            printerInfo["system_description"] = await self._snmp_get_async(
                transport, self.OID_SYS_DESCR
            ) or "Unknown"
            printerInfo["device_description"] = await self._snmp_get_async(
                transport, self.OID_DEVICE_DESC
            ) or "Unknown"

            # Pages printed
            totalPages = await self._snmp_get_async(transport, self.OID_TOTAL_PAGES)
            printerInfo["pages_printed"] = totalPages or "Unknown"

            # Uptime
            uptime = await self._snmp_get_async(transport, self.OID_SYS_UPTIME)
            if uptime:
                try:
                    uptimeTicks = int(uptime)
                    uptimeSeconds = uptimeTicks // 100
                    uptimeDays = uptimeSeconds // 86400
                    uptimeHours = (uptimeSeconds % 86400) // 3600
                    uptimeMinutes = (uptimeSeconds % 3600) // 60
                    printerInfo["uptime"] = (
                        f"{uptimeDays}d {uptimeHours}h {uptimeMinutes}m"
                    )
                except ValueError:
                    printerInfo["uptime"] = uptime
            else:
                printerInfo["uptime"] = "Unknown"

            # Ink levels
            cyanLevel = await self._snmp_get_async(transport, self.OID_CYAN_LEVEL)
            magentaLevel = await self._snmp_get_async(transport, self.OID_MAGENTA_LEVEL)
            yellowLevel = await self._snmp_get_async(transport, self.OID_YELLOW_LEVEL)
            blackLevel = await self._snmp_get_async(transport, self.OID_BLACK_LEVEL)

            printerInfo["ink_levels"] = {
                "cyan": cyanLevel or "Unknown",
                "magenta": magentaLevel or "Unknown",
                "yellow": yellowLevel or "Unknown",
                "black": blackLevel or "Unknown",
            }

            # Network information
            printerInfo["ip_address"] = self.m_printerIp
            printerInfo["network_status"] = (
                "Connected" if printerInfo["model_name"] != "Unknown" else "Disconnected"
            )

            return printerInfo
        finally:
            close_method = getattr(transport, "close", None)
            if close_method:
                result = close_method()
                if asyncio.iscoroutine(result):
                    await result

    def _run_async(self, coroutine_factory, *args, **kwargs):
        """Execute an async coroutine factory safely from synchronous code."""

        try:
            return asyncio.run(coroutine_factory(*args, **kwargs))
        except RuntimeError as exc:
            if "event loop" in str(exc):
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    return loop.run_until_complete(coroutine_factory(*args, **kwargs))
                finally:
                    asyncio.set_event_loop(None)
                    loop.close()
            raise

    def collect_printer_info(self) -> Dict[str, Any]:
        """Collect all printer information via SNMP.

        Returns:
            Dict[str, Any]: Dictionary containing printer information.
        """
        logger.info(f"Collecting SNMP data from {self.m_printerIp}")
        printerInfo = self._run_async(self._collect_printer_info_async)
        logger.info("SNMP data collection completed")
        return printerInfo
