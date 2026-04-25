"""
Logging configuration.

Used by the FastAPI interface layer to log inbound webhook traffic.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("signal_api")
