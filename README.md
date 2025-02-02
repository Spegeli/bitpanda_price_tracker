I have created a custom integration to query the prices of coins/tokens from Bitpanda.com. The officially provided API by Bitpanda is used for this purpose. 

**Important**: Your wallets are not queried, only the current prices of the respective coins/tokens.

You can find this integration on GitHub: https://github.com/Spegeli/bitpanda_price_tracker

You need to manually load the "bitpanda_price_tracker" folder as it is into the "custom_components" folder. After restarting Home Assistant, you can add the "Bitpanda Price Tracker" via "Settings -> Devices & Services -> Add Integration".

There you can select the currency in which everything should be tracked, the interval for updates (I recommend the standard 5 minutes), and finally which coins/tokens you want to track. For each selected coin/token, a separate sensor will be created, e.g., BTC/EUR.

The currency can only be selected during creation, not during editing. So if you decide to switch everything to USD instead of EUR, you need to delete the configuration once via the UI and re-create it with your desired currency.

---

There is currently no changelog (for any future changes) and no HACS integration yet. Whether I will change this in the future remains to be seen.

You will need to check the repository yourself for any updates and what might have been changed, and manually perform the update if necessary.

I will try to provide information in this thread about the latest changes.

Questions, suggestions, and any wishes should be posted here and not on GitHub. On GitHub, please only report errors.

---

P.S. I am also working on a second integration to query the wallets, which will make it possible to track exactly which wallets you have on Bitpanda in Home Assistant, the number of coins, their value, etc. This is mostly finished and working, but I still want to make a few changes before I release it, so it will take a few more days.
