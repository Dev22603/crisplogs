# Plain text output (no colors) — ideal for CI and log files.
# Run: python examples/plain_output.py

from crisplogs import setup_logging

print("=== plain, no box ===")
logger = setup_logging(colored=False, name="plain")
logger.info("No colors, no box")
logger.warning("Clean for CI pipelines")

print("\n=== plain + short-fixed box ===")
logger = setup_logging(colored=False, style="short-fixed", width=80, name="plain-box")
logger.info("No colors, but boxed")
logger.error("Good for structured plain logs")

print("\n=== plain + long-boxed ===")
logger = setup_logging(colored=False, style="long-boxed", width=80, name="plain-long")
logger.info(
    "Word-wrapped without colors — great for log aggregators",
    extra={"env": "production", "region": "us-east-1"},
)
