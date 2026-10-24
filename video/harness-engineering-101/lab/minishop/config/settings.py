"""Settings for every environment. Values here are read once at import."""

ENV = "production"
CURRENCY = "KRW"
TAX_RATE = 0.10
FREE_SHIPPING_OVER = 50_000
SHIPPING_FEE = 3_000

DB_URL = "postgresql://shop@db.internal/minishop"
SEARCH_URL = "http://search.internal:9200"

# Outbound calls. Each entry is turned into a RetryPolicy by net.backoff.policy_from().
CATALOG_HTTP = {"timeout": 2.0, "attempts": 2, "base_delay": 0.2}
SEARCH_HTTP = {"timeout": 1.5, "attempts": 1, "base_delay": 0.0}
PAYMENT_HTTP = {"timeout": 8.0, "attempts": 4, "base_delay": 0.5, "max_delay": 4.0}
WEBHOOK_HTTP = {"timeout": 5.0, "attempts": 6, "base_delay": 1.0, "max_delay": 30.0}
WAREHOUSE_HTTP = {"timeout": 3.0, "attempts": 3, "base_delay": 0.3}

FEATURE_FLAGS = {
    "new_checkout": True,
    "saved_carts": False,
    "gift_cards": True,
}
