# Copyright 2009-2012 Yelp
# Copyright 2013 Steve Johnson and David Marin
# Copyright 2014 Yelp and Contributors
# Copyright 2015-2018 Yelp
# Copyright 2019 Yelp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for parsing errors, and status messages."""
import logging
import re
from functools import wraps
from io import BytesIO
from os.path import abspath

from example_demo.mrjob.py2 import ParseResult
from example_demo.mrjob.py2 import pathname2url
from example_demo.mrjob.py2 import to_unicode
from example_demo.mrjob.py2 import urljoin
from example_demo.mrjob.py2 import urlparse as urlparse_buggy

log = logging.getLogger(__name__)


### URI PARSING ###

def is_uri(uri):
    r"""Return True if *uri* is a URI and contains ``://``
    (we only care about URIs that can describe files)

    .. versionchanged:: 0.5.7

       used to recognize anything containing a colon as a URI
       unless it was a Windows path (``C:\...``).
    """
    return '://' in uri and bool(urlparse(uri).scheme)

def to_uri(path_or_uri):
    """If *path_or_uri* is not a URI already, convert it to a ``file:///``
    URI."""
    if is_uri(path_or_uri):
        return path_or_uri
    else:
        return urljoin('file:', pathname2url(abspath(path_or_uri)))


@wraps(urlparse_buggy)
def urlparse(urlstring, scheme='', allow_fragments=True, *args, **kwargs):
    """A wrapper for :py:func:`urlparse.urlparse` that splits the fragment
    correctly in all URIs, not just Web-related ones.
    This behavior was fixed in the Python 2.7.4 standard library but we have
    to back-port it for previous versions.
    """
    (scheme, netloc, path, params, query, fragment) = (
        urlparse_buggy(urlstring, scheme, allow_fragments, *args, **kwargs))

    if allow_fragments and '#' in path and not fragment:
        path, fragment = path.split('#', 1)

    return ParseResult(scheme, netloc, path, params, query, fragment)
