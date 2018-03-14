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
```

this `stocks.vgplot.line().spec` is a JSON object representing a timeseries of stock prices. It is too complicated to read manually.

Import `vegascope` and create a `LocalCanvas`. It prompts you with a URL to copy into your web browser. Once that is loaded, 

```python
>>> import vegascope
>>> canvas = vegascope.LocalCanvas()
Point web browser at: http://localhost:40142
127.0.0.1 connected

>>> canvas(stocks.vgplot.line().spec)
```

![](example.png)
