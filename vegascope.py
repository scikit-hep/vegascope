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

import errno
import json
import socket
import sys
import threading
import time

if sys.version_info[0] < 3:
    import SimpleHTTPServer
    import SocketServer
    from urllib2 import urlopen
    string_types = (unicode, str)
    class BrokenPipeError(Exception): pass
else:
    import http.server as SimpleHTTPServer
    import socketserver as SocketServer
    from urllib.request import urlopen
    string_types = (str, bytes)

class Canvas(object):
    def __init__(self, title=None, initial=None, bind="localhost", port=0):
        if title is None:
            self.title = "VegaScope"
        else:
            self.title = title

        if initial is None:
            self(Canvas._default)
        else:
            self(initial)

        canvas = self

        class FakeFile(object):
            @property
            def closed(self):
                return True
            def close(self):
                pass
            def flush(self):
                pass

        class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    page = canvas._template.replace("VEGAVIEW", "#vegaview").replace("TITLE", canvas.title).replace("SPEC", canvas.spec).encode("utf-8")
                    self.wfile.write(page)

                elif self.path == "/favicon.ico":
                    self.send_response(200)
                    self.send_header("Content-type", "image/x-icon")
                    self.end_headers()
                    self.wfile.write(canvas._favicon)
                    
                elif self.path == "/update":
                    self.send_response(200)
                    self.send_header("Content-type", "text/event-stream")
                    self.end_headers()
                    spec = canvas.spec
                    try:
                        while not self.wfile.closed:
                            time.sleep(0.1)
                            if canvas.spec is None:
                                break
                            elif spec != canvas.spec:
                                spec = canvas.spec
                                self.wfile.write("data: {0}\n\n".format(spec).encode("utf-8"))
                            else:
                                self.wfile.write(":\n\n".encode("utf-8"))
                            self.wfile.flush()

                    except socket.error as err:
                        if isinstance(err, BrokenPipeError) or err[0] == errno.EPIPE:
                            self.wfile = FakeFile()
                        else:
                            raise

        self.httpd = SocketServer.ThreadingTCPServer((bind, port), HTTPHandler)
        self.host, self.port = self.httpd.server_address

        self.thread = threading.Thread(name=self.title, target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def __call__(self, spec):
        if isinstance(spec, string_types):
            self.spec = json.dumps(json.loads(spec))   # make sure it's a one-liner
        else:
            self.spec = json.dumps(spec)

    def close(self):
        self.spec = None
        self.httpd.shutdown()
        self.httpd.server_close()

    @property
    def closed(self):
        return self.spec is None

    def __del__(self):
        if not self.closed:
            self.close()

    @property
    def external_ip(self):
        return urlopen("https://v4.ident.me").read().decode("ascii").strip()

    @property
    def address(self):
        return "http://{0}:{1}".format(self.external_ip, self.port)

    _default = {
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
            "zero": True,
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
                "stroke": {"value": "#888888"}
              },
              "update": {
                "fill": {"value": "#ffcc00"}
              }
            }
          }
        ]
    }
    
    _template = u"""
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
var spec = SPEC;

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

var eventSource = new EventSource("/update");
eventSource.onmessage = function(event) {
    var spec = JSON.parse(event.data);
    view = new vega.View(vega.parse(spec)).renderer("svg").initialize("VEGAVIEW").run();
};

    </script>
  </body>
</html>
"""

    _favicon = b"\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00 \x00h\x04\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x80\x80\x80\xff\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\x80\x80\x80\xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x80\x80\x80\xff\x00\xcc\xff\x15\xcc\xcc\xcc\x00\x80\x80\x80\x00\x80\x80\x80\xff\x80\x80\x80\xff\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\x00\xcc\xff\x15\x80\x80\x80\xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x80\x80\x80\xff\x00\xcc\xff\xff\x80\x80\x80\xff\xcc\xcc\xcc\x00\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\xcc\xcc\xcc\x00\x80\x80\x80\xff\x00\xcc\xff\xff\x80\x80\x80\xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\xff\xff\xff\x00\x00\xcc\xff\x07\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff}\x80\x81\xff\x00\xcc\xff\xff\x00\xcc\xff\xff~\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x0b\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x15\x00\xcc\xff\x0f\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x0c\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\x00\xcc\xff\x12\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x0c\xcc\xcc\xcc\x00\xcc\xcc\xcc\x00\x00\xcc\xff\x12\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x0c\x00\xcc\xff\x0e\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x0b\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x00\xcc\xff\x18\xff\xff\xff\x00\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x00\xcc\xff\xff\x80\x80\x80\xff\x80\x80\x80\xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x00\xcc\xff\x05\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\xcc\xff\x0f\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xef\xf7\x00\x00\xeew\x00\x00\xc4#\x00\x00\x80\x01\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x01\x80\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x80\x01\x00\x00\xc0\x03\x00\x00\xe0\x07\x00\x00\xf8\x1f\x00\x00"
