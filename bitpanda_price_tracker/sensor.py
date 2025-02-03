from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_SYMBOLS, CONF_CURRENCY, CONF_UPDATE_INTERVAL, CURRENCY_ICONS
from .api import async_fetch_bitpanda_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensors from config entry."""
    currency = entry.data[CONF_CURRENCY]
    symbols = entry.options.get(CONF_SYMBOLS, entry.data.get(CONF_SYMBOLS, []))
    update_interval = float(entry.options.get(CONF_UPDATE_INTERVAL, 5))

    coordinator = BitpandaDataUpdateCoordinator(hass, currency, update_interval)
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.data:
        raise ConfigEntryNotReady("No data received from Bitpanda API")

    entities = []
    for symbol in symbols:
        if symbol in coordinator.data:
            entities.append(BitpandaPriceSensor(coordinator, symbol, currency))
        else:
            _LOGGER.warning("Symbol %s not found in Bitpanda API data", symbol)

    async_add_entities(entities)

    # Registriere den Update-Listener für Optionen-Änderungen
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle updated options."""
    await hass.config_entries.async_reload(entry.entry_id)

class BitpandaDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Bitpanda API."""

    def __init__(self, hass: HomeAssistant, currency: str, update_interval_minutes: float) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval_minutes)
        )
        self.currency = currency
        self.next_update = dt_util.utcnow() + self.update_interval

    async def _async_update_data(self) -> dict:
        """Fetch data from API using the external api.py module."""
        try:
            data = await async_fetch_bitpanda_data(self.hass, self.currency)
            return data
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err
        finally:
            # Aktualisiere den Zeitpunkt der nächsten Aktualisierung
            self.next_update = dt_util.utcnow() + self.update_interval

class BitpandaPriceSensor(SensorEntity):
    """Representation of a Bitpanda price sensor."""
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = False  # We use DataUpdateCoordinator

    def __init__(self, coordinator: BitpandaDataUpdateCoordinator, symbol: str, currency: str) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.symbol = symbol
        self._currency = currency
        self._attr_name = f"Bitpanda Price Tracker {symbol}/{currency}"
        self._attr_unique_id = f"{DOMAIN}_{symbol}_{currency}"
        self._attr_icon = CURRENCY_ICONS.get(currency, "mdi:currency-usd")
        self._attr_native_unit_of_measurement = currency

    @property
    def native_value(self):
        """Return current price."""
        return self.coordinator.data.get(self.symbol, {}).get("price")

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        data = self.coordinator.data.get(self.symbol, {})
        return {
            "last_update": data.get("last_updated"),
            "next_update": dt_util.as_local(self.coordinator.next_update).isoformat(),
            "symbol": self.symbol,
            "update_interval": str(self.coordinator.update_interval)
        }

    async def async_added_to_hass(self) -> None:
        """Register update listener."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
