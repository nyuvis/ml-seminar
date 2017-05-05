#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import io
import re
import os
import csv
import sys
import json
import pytz
import zlib

from dateutil.parser import parse as tparse
from datetime import datetime, timedelta, tzinfo

_compute_self = "total_seconds" not in dir(timedelta(seconds=1))
_tz = pytz.timezone('US/Eastern')
_epoch = datetime(year=1970, month=1, day=1, tzinfo=_tz)
_day_seconds = 24 * 3600
_milli = 10**6
def mktime(dt):
    if dt.tzinfo is None:
        dt = datetime(year=dt.year, month=dt.month, day=dt.day, tzinfo=_tz)
    if not _compute_self:
        res = (dt - _epoch).total_seconds()
    else:
        td = dt - _epoch
        res = (td.microseconds + (td.seconds + td.days * _day_seconds) * _milli) / _milli
    return int(res - res % _day_seconds)

def chk(doc, field):
    return field in doc and doc[field]

def add_misc_links(appendix, docs):
    for app in docs:
        appendix.append(u"""<a href="{0}">[{1}]</a>""".format(app["href"], app["name"]))

def create_media(doc):
    doc.sort(key=lambda t: (tparse(t['date']), t['title']), reverse=True)
    content = u''
    for e in doc:
        dt = tparse(e['date'])
        entry_id = u"entry{:08x}".format(zlib.crc32(u"{0}_{1}".format(e['title'], mktime(dt)).encode('utf-8')) & 0xffffffff)
        appendix = []
        add_misc_links(appendix, e["materials"])
        authors = u''
        for p in e["presenters"]:
            if authors:
                authors += u"<span>, </span>"
            if chk(p, "href"):
                authors += u"""<a href="{0}">{1}</a>""".format(p["href"], p["name"])
            else:
                authors += u"""<span>{0}</span>""".format(p["name"])
        entry = u"""
        <h2>
          <a href="#{0}" class="anchor" aria-hidden="true"><i class="fa fa-thumb-tack fa-1" aria-hidden="true"></i></a>
          {1}
        </h2>
        <div class="talk_info">
          <h3>{2}</h3>
          <div class="presenter_info">
            {3}
          </div>
          <div class="materials">
            {4}
          </div>
        </div>
        """.format(
            entry_id,
            e['title'],
            dt.strftime("%a, %B %d %Y"),
            authors,
            " ".join(appendix) if appendix else "",
        )
        content += u"""
        <div class="talk_container" id="{0}">
          {1}
        </div>
        """.format(entry_id, entry)
    return content

def apply_template(tmpl, docs):
    with io.open(tmpl, 'r', encoding='utf-8') as tf:
        content = tf.read()
    with io.open(docs, 'r', encoding='utf-8') as df:
        data = df.read()

        def sanitize(m):
            return m.group(0).replace('\n', '\\n')

        data = re.sub(u'''"([^"]|\\\\")*":\s*"([^"]|\\\\")*"''', sanitize, data)
        dobj = json.loads(data, encoding='utf-8')
    doc_objs = dobj["events"]
    media = create_media(doc_objs)
    return content.format(
        name=dobj["name"].strip(),
        description=dobj["description"].strip(),
        content=media,
    )

def usage():
    print("""
usage: {0} [-h] [--out <file>] --documents <file> --template <file>
-h: print help
--documents <file>: specifies the documents input
--template <file>: specifies the template file
--out <file>: specifies the output file. default is STD_OUT.
""".strip().format(sys.argv[0]), file=sys.stderr)
    exit(1)

if __name__ == '__main__':
    tmpl = None
    docs = None
    out = '-'
    args = sys.argv[:]
    args.pop(0)
    while args:
        arg = args.pop(0)
        if arg == '-h':
            usage()
        elif arg == '--template':
            if not args:
                print("--template requires argument", file=sys.stderr)
                usage()
            tmpl = args.pop(0)
        elif arg == '--out':
            if not args:
                print("--out requires argument", file=sys.stderr)
                usage()
            out = args.pop(0)
        elif arg == '--documents':
            if not args:
                print("--documents requires argument", file=sys.stderr)
                usage()
            docs = args.pop(0)
        else:
            print('unrecognized argument: {0}'.format(arg), file=sys.stderr)
            usage()
    if tmpl is None or docs is None:
        print('input is underspecified', file=sys.stderr)
        usage()
    content = apply_template(tmpl, docs)
    if out != '-':
        with io.open(out, 'w', encoding='utf-8') as outf:
            outf.write(content)
    else:
        sys.stdout.write(content)
        sys.stdout.flush()
