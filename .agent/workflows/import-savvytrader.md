---
description: How to automate the importing of SavvyTrader portfolio data
---

*See [SavvyTrader API Documentation](../../docs/savvytrader-api.md) for full endpoint details.*

To import the latest SavvyTrader data, follow these steps:

1. **Login and Get Token**:
   - Open SavvyTrader in your browser and log in at `https://savvytrader.com/mingdom/mingdom-capital`.
   - Open Developer Tools -> Application -> Local Storage -> `https://savvytrader.com`.
   - Look for a key starting with `CognitoIdentityServiceProvider...idToken`.
   - Copy the value (the full JWT token).

2. **Fetch Data**:
   Run the utility script with the token:
   ```bash
   ./venv/bin/python scripts/fetch_savvytrader.py "<TOKEN>"
   ```
   *This performs a full data capture (valuations, holdings/prices, cost basis, metadata) to `data/savvytrader/YYYY-MM-DD_HHMMSS/` and stages the primary files in `data/import/`.*

3. **Process Import**:
   Run the following command:
   ```bash
   make import
   ```
   *Note: `make import` will pick up both the valuations and holdings files, update the canonical `data/valuations.json` and `data/prices.json`, and archive the sources.*

// turbo
4. **Verify**:
   ```bash
   make report
   ```

---
**Note for AI Agent**:
You can automate steps 1 & 2 using the `browser_subagent`:
1. Navigate to `https://savvytrader.com/mingdom/mingdom-capital` and extract the `idToken` from localStorage.
2. Pass the token to `scripts/fetch_savvytrader.py`.
3. The script will handle all API calls and data organization automatically.
