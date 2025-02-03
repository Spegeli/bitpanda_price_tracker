import logging

from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import BITPANDA_API_URL

_LOGGER = logging.getLogger(__name__)

async def async_fetch_bitpanda_data(hass, currency: str) -> dict:
    """
    Fetch data from the Bitpanda API.
    
    Returns:
        A dictionary where each key is a symbol and the value is a dictionary
        with keys "price" (the price in the given currency) and "last_updated" (the ISO timestamp).
    """
    session = async_get_clientsession(hass)
    try:
        async with session.get(BITPANDA_API_URL, timeout=15) as response:
            response.raise_for_status()
            data = await response.json()
            result = {
                symbol: {
                    "price": details.get(currency),
                    "last_updated": dt_util.utcnow().isoformat()
                }
                for symbol, details in data.items()
                if currency in details
            }
            return result
    except Exception as err:
        _LOGGER.error("Error fetching data from Bitpanda API: %s", err)
        raise

async def async_fetch_valid_symbols(hass, currency: str) -> list[str]:
    """
    Fetch valid symbols from the Bitpanda API based on the provided currency.
    
    Returns:
        A sorted list of valid symbols.
    """
    try:
        data = await async_fetch_bitpanda_data(hass, currency)
        return sorted(data.keys())
    except Exception as err:
        _LOGGER.error("Error fetching valid symbols: %s", err)
        return []
