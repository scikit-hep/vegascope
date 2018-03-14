VegaScope
=========

VegaScope is a minimal viewer of [Vega](https://vega.github.io/vega/) and [Vega-Lite](https://vega.github.io/vega-lite/) graphics from Python. The Python process generating the graphics does not need to be on the same machine as the web browser viewing them.

VegaScope has zero dependencies and can be installed as a single file.

```bash
pip install vegascope
```

or copy [vegascope.py](https://raw.githubusercontent.com/diana-hep/vegascope/master/vegascope.py) to the desired location.

Example
-------

Suppose that we have a process that generates Vega graphics, such as [PdVega](https://jakevdp.github.io/pdvega/) (example requires pip packages `pdvega` and `vega_datasets`):

```python
>>> from vega_datasets import data
>>> import pdvega
>>> stocks = data.stocks(pivoted=True)
>>> stocks.vgplot.line().spec
```
```
{'selection': {'grid': {'bind': 'scales', 'type': 'interval'}}, 'encoding': {'y': {'field': 'value', 'ty
pe': 'quantitative'}, 'x': {'field': 'date', 'type': 'temporal'}, 'color': {'field': 'variable', 'type':
 'nominal'}}, 'height': 300, 'width': 450, '$schema': 'https://vega.github.io/schema/vega-lite/v2.json',
 'mark': 'line', 'data': {'values': [{'date': '2000-01-01', 'variable': 'AAPL', 'value': 25.94}, {'date'
...
```

This `stocks.vgplot.line().spec` is a JSON object representing a timeseries of stock prices. It is too complicated to read manually.

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

Or a JSON object as nested Python dicts. It supports the Vega 3 and Vega-Lite 2 specifications.

Interactive features
--------------------

In addition to any interactivity the Vega graphic may have on its own, VegaScope has five features:

   - *Save as PNG:* create a PNG image in your downloads folder (file name is the current title + `.png`).
   - *Save as SVG:* create a SVG image in your downloads folder (ending in `.svg`). SVG files can be edited as vector graphics (you can move the data points around, add annotations) and converted losslessly to sharp PDFs. My favorite tool for editing SVG and converting to PDF is [Inkscape](https://inkscape.org/).
   - *Zoom buttons/box:* scale the graphic on the web page. Does not affect saved file size.
   - *View source:* to see the raw JSON.
   - *View in editor:* to edit and view the graphic in the official [Vega editor](https://vega.github.io/editor). This editor gives you a lot of insight into how Vega declarations translate into graphics, but it's not optimal for rapid-fire plotting.

You may want to save graphics programmatically (in a loop, for instance), so the VegaScope canvas has methods for invoking this from the server:

```python
>>> canvas.png(graphic, title="filename")   # saves filename.png
>>> canvas.svg(graphic, title="filename")   # saves filename.svg
```

However, your web browser will probably interpret this as a pop-up. You usually don't want web servers to save files on your disk! In most web browsers, an indicator appears in the location bar the first time you try to write a file programmatically; select it and allow pop-ups for this server.

*Hint:* your web browser will remember the setting if you always use the same port number.

```python
>>> canvas = vegascope.LocalCanvas(port=12345)
```

Remote viewing
--------------


