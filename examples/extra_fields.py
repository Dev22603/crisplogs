# Structured data logging with extra fields.
# Run: python examples/extra_fields.py

from crisplogs import setup_logging

print("=== inline format (default) ===")
logger = setup_logging(style="long-boxed", extra_format="inline", name="inline")
logger.info("User signed up", extra={"user_id": 1042, "email": "alice@example.com"})
logger.warning("Rate limit reached", extra={"ip": "203.0.113.5", "limit": 100})
logger.error("Payment failed", extra={"order_id": 9912, "amount": "$49.99"})

print("\n=== json format ===")
logger = setup_logging(extra_format="json", name="json-fmt")
logger.info("Order placed", extra={"order_id": 1234, "total": 59.99})

print("\n=== pretty format ===")
logger = setup_logging(style="long-boxed", extra_format="pretty", name="pretty-fmt")
logger.info("Config loaded", extra={"host": "localhost", "port": 5432, "db": "myapp"})
