"""Notification module for sending alerts to ntfy.sh.

This module handles sending notifications to ntfy.sh service.
"""

import logging
from typing import Optional
import requests


logger = logging.getLogger(__name__)


class Notifier:
    """Notifier for sending alerts to ntfy.sh."""

    NTFY_BASE_URL = "https://ntfy.sh"

    def __init__(self, channel: str) -> None:
        """Initialize notifier.

        Args:
            channel: The ntfy.sh channel to send notifications to.
        """
        self.m_channel: str = channel
        self.m_url: str = f"{self.NTFY_BASE_URL}/{self.m_channel}"

    def send_notification(
        self, 
        message: str, 
        title: Optional[str] = None, 
        priority: str = "default",
        tags: Optional[list] = None
    ) -> bool:
        """Send a notification to ntfy.sh.

        Args:
            message: The notification message.
            title: Optional title for the notification.
            priority: Priority level (min, low, default, high, max).
            tags: Optional list of tags/emojis.

        Returns:
            bool: True if notification was sent successfully, False otherwise.
        """
        try:
            headers = {}
            if title:
                headers["Title"] = title
            if priority:
                headers["Priority"] = priority
            if tags:
                headers["Tags"] = ",".join(tags)

            logger.info(f"Sending notification to {self.m_url}")
            logger.debug(f"Message: {message}")

            response = requests.post(
                self.m_url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send notification: HTTP {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Notification request timed out")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {e}")
            return False

    def send_error(self, message: str, error: Optional[Exception] = None) -> bool:
        """Send an error notification.

        Args:
            message: The error message.
            error: Optional exception object.

        Returns:
            bool: True if notification was sent successfully, False otherwise.
        """
        errorMessage = message
        if error:
            errorMessage += f"\n\nError details: {str(error)}"

        return self.send_notification(
            errorMessage,
            title="Printer Maintenance Error",
            priority="high",
            tags=["warning", "printer"]
        )

    def send_success(self, message: str) -> bool:
        """Send a success notification.

        Args:
            message: The success message.

        Returns:
            bool: True if notification was sent successfully, False otherwise.
        """
        return self.send_notification(
            message,
            title="Printer Maintenance Success",
            priority="default",
            tags=["white_check_mark", "printer"]
        )
