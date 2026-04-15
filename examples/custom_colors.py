# Custom color overrides per log level.
# Run: python examples/custom_colors.py

from crisplogs import setup_logging

logger = setup_logging(
    log_colors={
        "DEBUG": "thin_white",
        "INFO": "bold_green",
        "WARNING": "bold_yellow",
        "ERROR": "bold_red,bg_white",
        "CRITICAL": "bold_white,bg_red",
    }
)

logger.debug("Thin white debug")
logger.info("Bold green info")
logger.warning("Bold yellow warning")
logger.error("Bold red on white background error")
logger.critical("Bold white on red background critical")
