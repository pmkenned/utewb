#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os


def fetchBacklog(channels, skip_existing = True):

    for c in channels:

        dest_file = '../channels/%s/videos.json' % c['id']

        sys.stdout.write('channel: %s (%s)' % (c['id'], c['title']))
        sys.stdout.flush()

        os.makedirs(c['id'], exist_ok=True)

        if os.path.isfile(dest_file):
            if skip_existing:
                sys.stdout.write(' skipping\n')
                continue

        playlist = 'UU' + c['id'][2:]

        if False:
            result = subprocess.run(['youtube-dl', 'https://www.youtube.com/playlist?list=%s' % playlist, '--flat-playlist', '--dump-single-json'], capture_output=True, text=True)

            json_txt = result.stdout.replace('},', '},\n')

            sys.stdout.write('.\n')
            with open(dest_file, 'w') as fh:
                fh.write(json_txt)
        else:
            with open(dest_file, 'r') as fh:
                json_text = fh.read()

        with open('../channels/%s/index.html' % c['id'], 'w') as fh:
            output = ''
            output += r"""<!DOCTYPE html>
<html>
    <head>
        <title>TODO</title>
    </head>
    <body>
"""

            videos = json.loads(json_text)['entries']
            for v in videos:
                output += '<li><a href="https://www.youtube.com/watch?v=%s">%s</a></li>\n' % (v['url'], v['title'])

            output += r"""
        <ul>

        </ul>
    </body>
</html>"""
            fh.write(output)


# TODO: allow getting list of channels from stdin?
def main():
    if len(sys.argv) < 2:
        sys.stderr.write('usage: %s [FILE]\n' % sys.argv[0])
        exit(1)
    channels = json.loads(open(sys.argv[1]).read())['channels']
    fetchBacklog(channels)

if __name__ == "__main__":
    main()
