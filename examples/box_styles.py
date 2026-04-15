# All three box styles side by side.
# Run: python examples/box_styles.py

from crisplogs import setup_logging

print("=== short-fixed ===")
logger = setup_logging(style="short-fixed", width=90, name="fixed")
logger.info("Server started on port 8000")
logger.warning("Disk usage at 85%")

print("\n=== short-dynamic ===")
logger = setup_logging(style="short-dynamic", name="dynamic")
logger.info("Server started on port 8000")
logger.warning("Disk usage at 85%")

print("\n=== long-boxed ===")
logger = setup_logging(style="long-boxed", width=90, name="long")
logger.info("Server started on port 8000")
logger.warning(
    "This is a longer message that will be word-wrapped neatly inside the box "
    "without breaking any words in the middle.",
    extra={"host": "db-01", "usage": "85%"},
)
