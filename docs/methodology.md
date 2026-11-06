# SalesLens methodology

## Scope

SalesLens studies historical retail transactions. It is a descriptive analytics project, not a forecasting or causal-inference system.

## Cleaning rules

- Remove exact duplicate rows.
- Parse invoice dates and numeric fields.
- Exclude cancellation invoices (invoice numbers beginning with `C`) from completed-sales KPIs.
- Exclude non-positive quantity or unit price from completed-sales KPIs.
- Keep transactions with missing customer identifiers in revenue analysis; exclude them only from customer-level RFM analysis.
- Calculate line revenue as `Quantity × UnitPrice`.

## Metrics

- Revenue: sum of valid line revenue, in GBP.
- Units sold: sum of valid positive quantities.
- Invoices: distinct invoice numbers.
- Average order value: mean of invoice-level revenue totals.
- RFM: Recency = days since last purchase relative to one day after the latest transaction; Frequency = distinct invoices; Monetary = summed revenue.

## Customer segment rules

The project uses transparent median-based rules rather than a machine-learning clustering model. Segment names are descriptive labels, not a validated marketing classification.

## Limitations

The included sample is synthetic. For portfolio conclusions, use the full official UCI data. The dataset covers one retailer and a historical period in 2010–2011, so findings should not be generalised to today's entire retail market.
