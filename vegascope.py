#!/usr/bin/env python

# Copyright (c) 2018, DIANA-HEP
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import threading
import SimpleHTTPServer
import SocketServer
import time

TEMPLATE = u"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/vega@3.2.1"></script>
    <title id="title">TITLE</title>
  </head>
  <body>
    <div style="text-align: center">
      <div style="display: inline-block; text-align: center">
        <div style="display: inline-block; width: 400px; margin-top: 10px; margin-bottom: 10px;">
          <button id="png" style="float: left">Save as PNG</button>
          <button id="plus">+</button>
          <input  id="zoom" type="text" value="100" size="4" style="text-align: right">%
          <button id="minus">\u2212</button>
          <button id="svg" style="float: right">Save as SVG</button>
        </div>

        <div id="viewer" style="transform: scale(1.0); transform-origin: 50% 0%">
          <div id="vegaview"></div>
        </div>
      </div>
    </div>
    <script type="text/javascript">

var eventSource = new EventSource("/new");
eventSource.onmessage = function(event) {
    event.data;
};

function setzoom() {
    var s = Number(document.getElementById("zoom").value);
    if (isNaN(s)  ||  s <= 0) {
        document.getElementById("zoom").value = 100;
        s = 100;
    }
    document.getElementById("viewer").style.transform = "scale(" + (s / 100.0) + ")";
}

document.getElementById("plus").addEventListener("click", function(event) {
    document.getElementById("zoom").value = (Math.round(Number(document.getElementById("zoom").value) / 20.0) + 1) * 20;
    setzoom();
});

document.getElementById("minus").addEventListener("click", function(event) {
    document.getElementById("zoom").value = Math.max(20, (Math.round(Number(document.getElementById("zoom").value) / 20.0) - 1) * 20);
    setzoom();
});

document.getElementById("zoom").addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        setzoom();
    }
});

var title = "TITLE";

var spec = {
  "$schema": "https://vega.github.io/schema/vega/v3.json",
  "width": 200,
  "height": 200,

  "data": [
    {
      "name": "table",
      "values": [20, 10, 20],
      "transform": [{"type": "pie", "field": "data"}]
    }
  ],

  "scales": [
    {
      "name": "r",
      "type": "sqrt",
      "domain": {"data": "table", "field": "data"},
      "zero": true,
      "range": [20, 100]
    }
  ],

  "marks": [
    {
      "type": "arc",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"field": {"group": "width"}, "mult": 0.5},
          "y": {"field": {"group": "height"}, "mult": 0.5},
          "startAngle": {"field": "startAngle"},
          "endAngle": {"field": "endAngle"},
          "innerRadius": {"value": 20},
          "outerRadius": {"scale": "r", "field": "data"},
          "stroke": {"value": "white"}
        },
        "update": {
          "fill": {"value": "lightgray"}
        }
      }
    }
  ]
};

var view = new vega.View(vega.parse(spec)).renderer("svg").initialize("VEGAVIEW").run();

document.getElementById("png").addEventListener("click", function(event) {
    view.toImageURL("png").then(function(url) {
        var link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("target", "_blank");
        link.setAttribute("download", title + ".png");
        link.dispatchEvent(new MouseEvent("click"));
    }).catch(function(error) { alert(error); });
});

document.getElementById("svg").addEventListener("click", function(event) {
    view.toImageURL("svg").then(function(url) {
        var link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("target", "_blank");
        link.setAttribute("download", title + ".svg");
        link.dispatchEvent(new MouseEvent("click"));
    }).catch(function(error) { alert(error); });
});

    </script>
  </body>
</html>
"""

TEMPLATE = TEMPLATE.replace("VEGAVIEW", "#vegaview")

class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(TEMPLATE.encode("utf-8"))
        elif self.path == "/new":
            self.send_response(200)
            self.send_header("Content-type", "text/event-stream")
            self.end_headers()
            while True:
                self.wfile.write("data: blah\n\n")
                self.wfile.flush()
                time.sleep(1)

httpd = SocketServer.TCPServer(("", 0), HTTPHandler)

print httpd.socket.getsockname()

httpd.serve_forever()
