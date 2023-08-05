# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014, Luke Maurits <luke@maurits.id.au>
# All rights reserved.
# With contributions from:
# * Chris Clark
#  * Klein Stephane
#  * John Filleau
# PTable is forked from original Google Code page in April, 2015, and now
# maintained by Kane Blueriver <kxxoling@gmail.com>.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# Taken from :
# https://github.com/kxxoling/PTable
# https://pypi.python.org/pypi/PTable
"""
Redefinitions
*************
"""
import sys


py3k = sys.version_info[0] >= 3

if py3k:
    str_types = (str, )
    unicode_ = str
    basestring_ = str
    itermap = map
    iterzip = zip
    uni_chr = chr
    from html.parser import HTMLParser
    import io as StringIO
else:
    unicode_ = unicode
    basestring_ = basestring
    str_types = (unicode, str)
    import itertools
    itermap = itertools.imap
    iterzip = itertools.izip
    uni_chr = unichr
    from HTMLParser import HTMLParser
    import StringIO

HTMLParser, StringIO


if py3k and sys.version_info[1] >= 2:
    from html import escape
else:
    from cgi import escape
escape
