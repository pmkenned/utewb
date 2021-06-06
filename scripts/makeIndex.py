#!/usr/bin/env python3
import subprocess
import json
import sys
import os.path

import checkFeeds

def makeIndex(channels, skip_existing = True, show_avatars = True, show_captions = True):

    output = ""

    output += r"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>utewb</title>
<style>
ul.channels {
    list-style-type: none;
}
ul.channels li {
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
        <section>
            <h3>Recent Uploads</h3>
            <ul class="recent">
"""

    recentUploads = checkFeeds.listRecentVideos(channels, update_feeds=False)

    for v in recentUploads:
        output += '<li><a href="https://www.youtube.com/watch?v=%s">%s</a></li>' % (v['url'], v['title'])

    output += r"""
            </ul>
        </section>
        <section>
            <h3>Channels</h3>
            <ul class="channels">
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
        </section>
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
