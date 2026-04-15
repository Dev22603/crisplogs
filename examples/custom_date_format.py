# Various date/time format examples.
# Run: python examples/custom_date_format.py

from crisplogs import setup_logging

print("=== time only ===")
logger = setup_logging(datefmt="%H:%M:%S", name="time-only")
logger.info("Short time format")

print("\n=== full datetime ===")
logger = setup_logging(datefmt="%Y-%m-%d %H:%M:%S", name="full-dt")
logger.info("Full datetime format")

print("\n=== European format ===")
logger = setup_logging(datefmt="%d/%m/%Y %H:%M", name="european")
logger.info("European date format")

print("\n=== 12-hour clock ===")
logger = setup_logging(datefmt="%I:%M %p", name="12hr")
logger.info("12-hour clock format")
