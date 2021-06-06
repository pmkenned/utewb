#!/usr/bin/env python3
import subprocess
import json
import sys
import os.path


def makeIndex(channels, skip_existing = True):

    output = ""

    output += r"""<!DOCTYPE html>
<html>
    <head>
        <title>TODO</title>
    </head>
    <body>
"""

    for c in channels:
        output += '<li><a href="channels/%s/index.html">%s</a></li>\n' % (c['id'], c['title'])

    output += r"""
        <ul>

        </ul>
    </body>
</html>"""

    with open('../index.html', 'w') as fh:
        fh.write(output)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('usage: %s [FILE]\n' % sys.argv[0])
        exit(1)
    channels = json.loads(open(sys.argv[1]).read())['channels']
    makeIndex(channels)

if __name__ == "__main__":
    main()
