from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector  # Import für Selector hinzugefügt
from typing import Any
import voluptuous as vol
import aiohttp
import logging

from .const import (
    DOMAIN,
    CONF_SYMBOLS,
    CONF_CURRENCY,
    BITPANDA_API_URL,
    CURRENCIES,
    DEFAULT_CURRENCY,
    CONF_UPDATE_INTERVAL,
    UPDATE_INTERVAL_OPTIONS
)

_LOGGER = logging.getLogger(__name__)

async def fetch_valid_symbols(currency: str) -> list[str]:
    """Fetch valid symbols from Bitpanda API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BITPANDA_API_URL, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                return sorted(
                    symbol for symbol, details in data.items()
                    if currency in details
                )
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.error("API error: %s", err)
        return []

class BitpandaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bitpanda."""

    VERSION = 1
    _currency: str = None
    _update_interval: str = None

    async def async_step_user(self, user_input: dict[str, Any] = None):
        """Handle the initial step."""
        errors = {}
        if user_input:
            self._currency = user_input[CONF_CURRENCY]
            if await fetch_valid_symbols(self._currency):
                return await self.async_step_update_interval()
            errors["base"] = "no_symbols"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CURRENCY, default=DEFAULT_CURRENCY): vol.In(CURRENCIES)
            }),
            errors=errors
        )

    async def async_step_update_interval(self, user_input: dict[str, Any] = None):
        """Handle update interval selection."""
        if user_input:
            self._update_interval = user_input[CONF_UPDATE_INTERVAL]
            return await self.async_step_symbols()

        return self.async_show_form(
            step_id="update_interval",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL, default="5"): vol.In(UPDATE_INTERVAL_OPTIONS)
            })
        )

    async def async_step_symbols(self, user_input: dict[str, Any] = None):
        """Handle symbol selection."""
        errors = {}
        valid_symbols = await fetch_valid_symbols(self._currency)

        if user_input and (selected := user_input.get(CONF_SYMBOLS)):
            return self.async_create_entry(
                title=f"Bitpanda Price Tracker ({self._currency})",
                data={
                    CONF_CURRENCY: self._currency,
                },
                options={
                    CONF_SYMBOLS: selected,
                    CONF_UPDATE_INTERVAL: self._update_interval
                }
            )

        if user_input:
            errors["base"] = "no_symbols_selected"

        selector_config = selector.SelectSelectorConfig(
            options=valid_symbols,
            multiple=True,
            mode=selector.SelectSelectorMode.DROPDOWN
        )

        return self.async_show_form(
            step_id="symbols",
            data_schema=vol.Schema({
                vol.Required(CONF_SYMBOLS): selector.SelectSelector(selector_config)
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BitpandaOptionsFlow()

class BitpandaOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow updates."""

    async def async_step_init(self, user_input: dict[str, Any] = None):
        """Manage the options."""
        # Initialisierung der Variablen
        self._currency = self.config_entry.data[CONF_CURRENCY]
        self._update_interval = self.config_entry.options.get(CONF_UPDATE_INTERVAL, "5")
        self._symbols = self.config_entry.options.get(CONF_SYMBOLS, [])

        return await self.async_step_update_interval()

    async def async_step_update_interval(self, user_input: dict[str, Any] = None):
        """Handle update interval selection."""
        if user_input:
            self._update_interval = user_input[CONF_UPDATE_INTERVAL]
            return await self.async_step_symbols()

        return self.async_show_form(
            step_id="update_interval",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL, default=self._update_interval): vol.In(UPDATE_INTERVAL_OPTIONS)
            })
        )

    async def async_step_symbols(self, user_input: dict[str, Any] = None):
        """Handle symbol selection."""
        valid_symbols = await fetch_valid_symbols(self._currency)

        if user_input and (selected := user_input.get(CONF_SYMBOLS)):
            self._symbols = selected
            return self.async_create_entry(
                title="",
                data={
                    CONF_SYMBOLS: self._symbols,
                    CONF_UPDATE_INTERVAL: self._update_interval
                }
            )

        selector_config = selector.SelectSelectorConfig(
            options=valid_symbols,
            multiple=True,
            mode=selector.SelectSelectorMode.DROPDOWN
        )

        return self.async_show_form(
            step_id="symbols",
            data_schema=vol.Schema({
                vol.Required(CONF_SYMBOLS, default=self._symbols): selector.SelectSelector(selector_config)
            })
        )
