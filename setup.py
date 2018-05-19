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

from setuptools import setup

def get_version():
    g = {}
    exec(open("vegascope.py").read(), g)
    return g["__version__"]

setup(name="vegascope",
      version = get_version(),
      py_modules=["vegascope"],
      description = "View Vega/Vega-Lite plots in your web browser from local or remote Python processes.",
      long_description = """VegaScope is a minimal viewer of `Vega <https://vega.github.io/vega/>`_ and `Vega-Lite <https://vega.github.io/vega-lite/>`_ graphics from Python. The Python process generating the graphics does not need to be on the same machine as the web browser viewing them.

VegaScope has zero dependencies and can be installed as a single file. It can be used as a Python library or as a shell command, watching a file or stdin.

To install, simply

.. code-block:: bash

    pip install vegascope

(with ``--user`` if not superuser) or copy the single `vegascope.py <https://raw.githubusercontent.com/diana-hep/vegascope/master/vegascope.py>`_ file to the desired location.

See `https://github.com/diana-hep/vegascope <https://github.com/diana-hep/vegascope>`_ for examples and documentation.""",
      author = "Jim Pivarski (DIANA-HEP)",
      author_email = "pivarski@fnal.gov",
      maintainer = "Jim Pivarski (DIANA-HEP)",
      maintainer_email = "pivarski@fnal.gov",
      url = "https://github.com/diana-hep/vegascope",
      download_url = "https://raw.githubusercontent.com/diana-hep/vegascope/master/vegascope.py",
      license = "BSD 3-clause",
      install_requires = [],
      classifiers = [
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Intended Audience :: Information Technology",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: BSD License",
          "Operating System :: MacOS",
          "Operating System :: POSIX",
          "Operating System :: Unix",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Information Analysis",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Software Development",
          "Topic :: Utilities",
          ],
      platforms = "Any",
      )
