# SavvyTrader API Documentation

This document outlines the API endpoints discovered during exploratory testing of the SavvyTrader platform for the Mingdom Capital portfolio (ID: `4737`). These endpoints are used to automate data collection for portfolio performance, holdings, and transactions.

## Authentication

All API requests require a `Bearer` token in the `Authorization` header. This token is an `idToken` provided by AWS Cognito.

- **Header**: `Authorization: Bearer <ID_TOKEN>`
- **Token Location**: Browser `localStorage` key starting with `CognitoIdentityServiceProvider...idToken`.

## Endpoints

### 1. Portfolio Performance (Historical Valuations)
Retrieve the daily historical valuation of the portfolio.

- **URL**: `https://api.savvytrader.com/core/portfolios/4737/valuations?range=all`
- **Method**: GET
- **Response**: Array of daily valuation objects.
- **Key Fields**:
  - `summaryDate`: ISO 8601 date.
  - `dailyValuation`: Total portfolio value for that day.
  - `dailyValuationDelta`: Change from the previous day.

### 2. Portfolio Holdings & Real-time Prices
Retrieve the current state of all holdings, including current market prices, cash balance, and subtotals. This response structure matches our `data/prices.json`.

- **URL**: `https://api.savvytrader.com/core/portfolios/4737/holdings/prices`
- **Method**: GET
- **Response**: Root object containing holdings, cash, and summary totals.
- **Key Fields**:
  - `holdings`: Array of stock positions.
    - `symbol`, `quantity`, `pricePerShare` (cost), `currentPricePerShare`, `totalPercentChange`, etc.
  - `cash`: Object containing `currentTotalPrice` and `currentAllocation`.
  - `subtotals`: Portfolio summary excluding cash.
  - `totals`: Portfolio summary including cash.

### 3. Transaction History (Activity)
Retrieve a paginated list of all buy/sell transactions.

- **URL**: `https://api.savvytrader.com/v2/core/portfolios/4737/transactions?page=1&limit=20`
- **Method**: GET
- **Parameters**:
  - `page`: Page number (starting at 1).
  - `limit`: Number of items per page.
- **Response**: Paginated object containing transaction records.
- **Key Fields**:
  - `transactionType`: "buy" or "sell".
  - `symbol`: Ticker symbol.
  - `quantity`: Number of shares.
  - `pricePerShare`: Execution price.
  - `executionDate`: ISO 8601 date of the trade.
- **Note**: As of 2026-01-07, this endpoint returns a 400 Bad Request error with `limit=200`. The parameter constraints may need adjustment or the endpoint may have changed. Further investigation needed.

### 4. Positions Overview (Cost Basis)
Retrieve the initial entry list for current positions (mostly for cost basis reference).

- **URL**: `https://api.savvytrader.com/core/portfolios/4737/holdings?range=all`
- **Method**: GET
- **Response**: Array of current positions with entry pricing.

### 5. Account Metadata
Retrieve basic information about the portfolio.

- **URL**: `https://api.savvytrader.com/core/portfolios/4737`
- **Method**: GET

---

## Implementation Notes for Browser Agents

Future agents should prioritize the following sequence for a full data import:
1.  **Valuations**: Use `.../valuations?range=all` to update `data/valuations.json`.
2.  **Prices**: Use `.../holdings/prices` to update `data/prices.json`.
3.  **Optional Activity**: Use `.../transactions` to track new trades since the last update.
