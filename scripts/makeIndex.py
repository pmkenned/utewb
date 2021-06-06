#!/usr/bin/env python3
import subprocess
import json
import sys
import os.path


def makeIndex(channels, skip_existing = True, show_avatars = True, show_captions = True):

    output = ""

    output += r"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>utewb</title>
<style>
ul {
    list-style-type: none;
}
li {
    display: inline-block;
}
.avatar {
    object-fit: cover;
    object-position: center;
    width: 48px;
}
</style>
    </head>
    <body>
        <ul>
"""

    for c in channels:
        if show_avatars:
            if show_captions:
                output += '<li><figure><a href="channels/%s/index.html" title="%s"><img class="avatar" src="channels/%s/avatar.jpg"></a><figcaption>%s</figcaption></figure></li>\n' % (c['id'], c['title'], c['id'], c['title'])
            else:
                output += '<li><a href="channels/%s/index.html" title="%s"><img class="avatar" src="channels/%s/avatar.jpg"></a></li>\n' % (c['id'], c['title'], c['id'])
        else:
            output += '<li><a href="channels/%s/index.html">%s</a></li>\n' % (c['id'], c['title'])

    output += r"""

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
    makeIndex(channels, show_captions=False)

if __name__ == "__main__":
    main()
