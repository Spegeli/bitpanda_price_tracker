DOMAIN = "bitpanda_price_tracker"
CONF_CURRENCY = "currency"
CONF_SYMBOLS = "symbols"
CONF_UPDATE_INTERVAL = "update_interval"

BITPANDA_API_URL = "https://api.bitpanda.com/v1/ticker"
DEFAULT_CURRENCY = "EUR"
CURRENCIES = ["EUR", "USD", "CHF"]

UPDATE_INTERVAL_OPTIONS = {
    "1": "1 Minute",
    "2.5": "2.5 Minutes",
    "5": "5 Minutes"
}

CURRENCY_ICONS = {
    "EUR": "mdi:currency-eur",
    "USD": "mdi:currency-usd",
    "CHF": "mdi:currency-fran"
}