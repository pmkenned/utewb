#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os
import re


def fetchBacklog(channels, skip_existing = True, get_thumbnails = False, make_index = True, replace_json = True):

    for c in channels:

        dest_file = '../channels/%s/videos.json' % c['id']

        sys.stdout.write('channel: %s (%s)' % (c['id'], c['title']))
        sys.stdout.flush()

        os.makedirs('../channels/%s' % c['id'], exist_ok=True)
        if get_thumbnails:
            os.makedirs('../channels/%s/thumbnails' % c['id'], exist_ok=True)

        if os.path.isfile(dest_file):
            if skip_existing:
                sys.stdout.write(' skipping\n')
                continue

        playlist = 'UU' + c['id'][2:]

        if replace_json:
            result = subprocess.run(['youtube-dl', 'https://www.youtube.com/playlist?list=%s' % playlist, '--flat-playlist', '--dump-single-json'], capture_output=True, text=True)

            json_txt = result.stdout.replace('},', '},\n')

            with open(dest_file, 'w') as fh:
                fh.write(json_txt)
        else:
            with open(dest_file, 'r') as fh:
                json_text = fh.read()

        sys.stdout.write('.\n')

        if make_index:
            with open('../channels/%s/index.html' % c['id'], 'w') as fh:
                output = ''
                output += r"""<!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>""" + c['title'] + """</title>
            <style>

ul {
    list-style-type: none;
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
        <ul>
    """

                videos = json.loads(json_text)['entries']

                ps = dict()
                wget_ps = dict()

                # TODO: check for errors when retrieving thumbnails
                if get_thumbnails:

                    # fire off youtube-dls
                    for v in videos:
                        dest_jpg = '../channels/%s/thumbnails/%s.jpg' % (c['id'], v['url'])
                        sys.stdout.write('getting thumbnail url for %s' % v['url'])
                        if os.path.isfile(dest_jpg):
                            print(' skipping')
                            continue
                        ps[v['url']] = subprocess.Popen(['youtube-dl', '--list-thumbnails', 'https://www.youtube.com/watch?v=%s' % v['url']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        sys.stdout.write('\n')

                    # fire off wgets
                    for v in videos:
                        sys.stdout.write('downloading thumbnail for %s' % v['url'])
                        dest_jpg = '../channels/%s/thumbnails/%s.jpg' % (c['id'], v['url'])
                        if os.path.isfile(dest_jpg):
                            print(' skipping')
                            continue
                        out, err = ps[v['url']].communicate()
                        thumbnail_url = re.sub(r'\?.*', '', re.split(r'\s+', out.decode().split('\n')[3])[-1])
                        wget_ps[v['url']] = subprocess.Popen(['wget', '-q', '-O', '../channels/%s/thumbnails/%s.jpg' % (c['id'], v['url']), thumbnail_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        sys.stdout.write('\n')

                    # wait for wgets to finish
                    for v in videos:
                        if os.path.isfile(dest_jpg):
                            continue
                        out, err = wget_ps[v['url']].communicate()
                        print('thumbnail for %s done' % v['url'])

                for v in videos:

                    if get_thumbnails:
                        output += '<li><figure><a href="https://www.youtube.com/watch?v=%s"><img class="thumbnail" src="thumbnails/%s.jpg"></a><figcaption>%s</figcaption></figure></li>\n' % (v['url'], v['url'], v['title'])
                    else:
                        output += '<li><a href="https://www.youtube.com/watch?v=%s">%s</a></li>\n' % (v['url'], v['title'])

                output += r"""
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
    fetchBacklog(channels[0:1], skip_existing = False, get_thumbnails = True, make_index = True, replace_json = False)

if __name__ == "__main__":
    main()
