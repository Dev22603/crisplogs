# Comprehensive demo — runs through all styles and features.
# Run: python examples/demo.py

from crisplogs import get_logger, setup_logging

SEP = "\n" + "=" * 60 + "\n"

print(SEP + "1. Colored default (no box)")
logger = setup_logging(name="demo1")
logger.debug("Loading configuration...")
logger.info("Server started on port 8000")
logger.warning("Disk usage at 85%")
logger.error("Failed to connect to database")
logger.critical("System is shutting down")

print(SEP + "2. short-fixed box")
logger = setup_logging(style="short-fixed", width=90, name="demo2")
logger.info("Fixed-width left-border box")
logger.error("Each entry wrapped in a box")

print(SEP + "3. short-dynamic box")
logger = setup_logging(style="short-dynamic", name="demo3")
logger.info("Auto-width full-border box")
logger.warning("Width adjusts to content")

print(SEP + "4. long-boxed")
logger = setup_logging(style="long-boxed", width=90, name="demo4")
logger.info(
    "Word-wrapped box — ideal for verbose logs with lots of context",
    extra={"user_id": 42, "action": "login", "ip": "203.0.113.5"},
)

print(SEP + "5. Plain (no colors, no box)")
logger = setup_logging(colored=False, name="demo5")
logger.info("Clean for CI and piped output")
logger.warning("No ANSI codes emitted")

print(SEP + "6. Plain + long-boxed")
logger = setup_logging(colored=False, style="long-boxed", width=80, name="demo6")
logger.info("Boxed without colors", extra={"env": "production"})

print(SEP + "7. Custom colors")
logger = setup_logging(
    log_colors={
        "DEBUG": "thin_white",
        "INFO": "bold_green",
        "WARNING": "bold_yellow",
        "ERROR": "bold_red,bg_white",
        "CRITICAL": "bold_white,bg_red",
    },
    name="demo7",
)
logger.info("Bold green info")
logger.critical("Bold white on red")

print(SEP + "8. Extra formats")
logger = setup_logging(extra_format="inline", name="demo8-inline")
logger.info("Inline extras", extra={"k": "v", "n": 42})

logger = setup_logging(extra_format="json", name="demo8-json")
logger.info("JSON extras", extra={"k": "v", "n": 42})

print(SEP + "9. Level filtering (WARNING+)")
logger = setup_logging(level="WARNING", name="demo9")
logger.debug("Hidden")
logger.info("Hidden")
logger.warning("Visible")

print(SEP + "10. Named loggers")
setup_logging(name="")  # configure root
db = get_logger("app.db")
http = get_logger("app.http")
db.info("Connected to PostgreSQL")
http.warning("Slow response 2.3s")
