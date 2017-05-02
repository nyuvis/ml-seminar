#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import io
import os
import sys
import pytz

from datetime import datetime

_tz = pytz.timezone('US/Eastern')
def create_sitemap(out, lines):
    out.write(u"""<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
""")
    out.flush()
    tmpl = u"""  <url>
    <loc>{base}{path}</loc>
    <lastmod>{mod}</lastmod>
  </url>
"""
    base = "https://nyuvis.github.io/ml-seminar/"
    for line in sorted(set(lines)):
        line = line.strip().lstrip('./')
        if not line:
            continue
        if line.startswith("."):
            continue
        if line.endswith(".js"):
            continue
        if line.endswith(".css"):
            continue
        if line.endswith(".json"):
            continue
        filename = line if line else "."
        if os.path.isdir(filename) and not os.path.exists(os.path.join(filename, 'index.html')):
            continue
        print("processing: {0}".format(line))
        mtime = datetime.fromtimestamp(os.path.getmtime(filename), tz=_tz).isoformat()
        out.write(tmpl.format(base=base, path=line, mod=mtime))
        out.flush()
    out.write(u"""</urlset>
""")
    out.flush()

def usage():
    print("""
usage: {0} [-h] <file>
-h: print help
<file>: specifies the output file
""".strip().format(sys.argv[0]), file=sys.stderr)
    exit(1)

if __name__ == '__main__':
    args = sys.argv[:]
    args.pop(0)
    if "-h" in args:
        usage()
    if len(args) != 1:
        usage()
    output = args[0]
    with io.open(output, 'w', encoding='utf-8') as f_out:
        create_sitemap(f_out, sys.stdin.readlines())
