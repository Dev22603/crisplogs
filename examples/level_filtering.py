# Level filtering — only WARNING and above appear.
# Run: python examples/level_filtering.py

from crisplogs import setup_logging

logger = setup_logging(level="WARNING", name="filtered")

logger.debug("Hidden debug")   # filtered out
logger.info("Hidden info")     # filtered out
logger.warning("Visible warning")
logger.error("Visible error")
logger.critical("Visible critical")
