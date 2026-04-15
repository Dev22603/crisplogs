# Named child loggers that inherit root logger configuration.
# Run: python examples/named_loggers.py

from crisplogs import get_logger, setup_logging

# Configure root logger once
setup_logging(colored=True, style="short-fixed", level="DEBUG")

# Child loggers inherit the root's handlers automatically
db = get_logger("app.db")
http = get_logger("app.http")
cache = get_logger("app.cache")

db.info("Connected to PostgreSQL")
http.info("GET /api/users 200")
cache.warning("Cache miss — falling back to DB")
db.error("Query timeout after 30s", extra={"query": "SELECT * FROM orders"})
