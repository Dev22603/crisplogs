# File logging with ANSI stripping and separate log levels.
# Run: python examples/file_logging.py
# Then: cat app.log

import os

from crisplogs import setup_logging

LOG_FILE = "app.log"

# Console shows DEBUG+, file only gets WARNING+
logger = setup_logging(
    colored=True,
    level="DEBUG",
    file=LOG_FILE,
    file_level="WARNING",
    name="file-demo",
)

logger.debug("Loading config (console only)")
logger.info("Server started (console only)")
logger.warning("Cache miss rate is high (console + file)")
logger.error("DB connection failed (console + file)", extra={"host": "db-01"})

print(f"\nLog file written to: {os.path.abspath(LOG_FILE)}")

# Close handlers before reading/deleting (required on Windows)
from crisplogs import remove_logger
remove_logger("file-demo")

print("File contents (no ANSI codes):")
print(open(LOG_FILE).read())

os.remove(LOG_FILE)
