VegaScope
=========

VegaScope is a minimal viewer of [Vega](https://vega.github.io/vega/) and [Vega-Lite](https://vega.github.io/vega-lite/) graphics from Python. The Python process generating the graphics does not need to be on the same machine as the web browser viewing them.

VegaScope has zero dependencies and can be installed as a single file.

```bash
pip install vegascope
```

or copy `vegascope.py` to the desired location.

Example
-------

Suppose that we have a process that generates Vega graphics, such as [PdVega](https://jakevdp.github.io/pdvega/) (requires pip packages `pdvega` and `vega_datasets`):

```python
>>> from vega_datasets import data
>>> import pdvega
>>> stocks = data.stocks(pivoted=True)
>>> stocks.vgplot.line().spec
{'selection': {'grid': {'bind': 'scales', 'type': 'interval'}}, 'encoding': {'y': {'field': 'value', 'type': 'quantitative'}, 'x': {'field': 'date', 'type': 'temporal'}, 'color': {'field': 'variable', 'type': 'nominal'}}, 'height': 300, 'width': 450, '$schema': 'https://vega.github.io/schema/vega-lite/v2.json', 'mark': 'line', 'data': {'values': [{'date': '2000-01-01', 'variable': 'AAPL', 'value': 25.94}, {'date': '2000-02-01', 'variable': 'AAPL', 'value': 28.66}, {'date': '2000-03-01', 'variable':
```

this `stocks.vgplot.line().spec` is a JSON object representing a timeseries of stock prices. It is too complicated to read manually.

Import `vegascope` and create a `LocalCanvas`. It prompts you with a URL to copy into your web browser. Every time the canvas is called as a function on a Vega graphic, the web page will be updated with the latest plot. There is no need to refresh your browser.

```python
>>> import vegascope
>>> canvas = vegascope.LocalCanvas()
Point web browser at: http://localhost:40142
127.0.0.1 connected

>>> canvas(stocks.vgplot.line().spec)
```

![](example.png)

PdVega was only used as an example; the graphic could have come from anywhere. It could be a URL string:

```python
>>> canvas("https://vega.github.io/vega/examples/stacked-bar-chart.vg.json")
```

Or a JSON string:

```python
>>> graphic = """{
...   "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
...   "description": "A simple bar chart with embedded data.",
...   "data": {
...     "values": [
...       {"a": "A","b": 28}, {"a": "B","b": 55}, {"a": "C","b": 43},
...       {"a": "D","b": 91}, {"a": "E","b": 81}, {"a": "F","b": 53},
...       {"a": "G","b": 19}, {"a": "H","b": 87}, {"a": "I","b": 52}
...     ]
...   },
...   "mark": "bar",
...   "encoding": {
...     "x": {"field": "a", "type": "ordinal"},
...     "y": {"field": "b", "type": "quantitative"}
...   }
... }"""
>>> canvas(graphic)
```

Or a JSON object as nested Python dicts. It can be 
