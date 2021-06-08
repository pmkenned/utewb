#!/usr/bin/env python3
import subprocess
import json
import sys
import os.path

import checkFeeds
import getBacklog

def makeIndex(channels, skip_existing = True, show_avatars = True, show_captions = True, show_thumbnails = True):

    getBacklog.getAvatars(channels)

    getBacklog.fetchBacklog(channels, replace_json = False)

    recentUploads = checkFeeds.listRecentVideos(channels, update_feeds=False)

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
ul.channels li {
    display: inline-block;
}
.avatar {
    object-fit: cover;
    object-position: center;
    width: 48px;
}
.thumbnail {
    object-fit: cover;
    object-position: center;
    height: 130px;
    width: 240px;
}
</style>
    </head>
    <body>
        <section>
            <h3>Recent Uploads</h3>
            <ul class="recent">
"""
    # TODO: sort by upload date
    # TODO: show channel name, etc and thumbnail
    # TODO: break into groups based on upload date
    for v in recentUploads:

        if show_thumbnails:
            if os.path.isfile('../channels/%s/thumbnails/%s.jpg' % (v['channel'], v['url'])):
                output += '<li><figure><a href="https://www.youtube.com/watch?v=%s"><img class="thumbnail" src="channels/%s/thumbnails/%s.jpg"></a><figcaption>%s</figcaption></figure></li>\n' % (v['url'], v['channel'], v['url'], v['title'])
            else:
                output += '<li><figure><a href="https://www.youtube.com/watch?v=%s">[no thumbnail]</a><figcaption>%s</figcaption></figure></li>\n' % (v['url'], v['title'])
        else:
            output += '<li><a href="https://www.youtube.com/watch?v=%s">%s</a></li>\n' % (v['url'], v['title'])

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
