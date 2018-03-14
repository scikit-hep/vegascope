VegaScope
=========




```python
>>> from vega_datasets import data
>>> import pdvega
>>> stocks = data.stocks(pivoted=True)
>>> stocks
symbol        AAPL    AMZN    GOOG     IBM   MSFT
date
2000-01-01   25.94   64.56     NaN  100.52  39.81
2000-02-01   28.66   68.87     NaN   92.11  36.35
2000-03-01   33.95   67.00     NaN  106.11  43.22
...            ...     ...     ...     ...    ...
2010-01-01  192.06  125.41  529.94  121.85  28.05
2010-02-01  204.62  118.40  526.80  127.16  28.67
2010-03-01  223.02  128.82  560.19  125.55  28.80

[123 rows x 5 columns]

>>> import vegascope
>>> c = vegascope.LocalCanvas()
Point web browser at: http://localhost:40142
127.0.0.1 connected

>>> c(stocks.vgplot.line().spec)
```
