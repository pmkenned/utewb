#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os
import re

def getAvatar(channel_id, output_file = 'avatar.jpg'):
    channel_url = 'https://www.youtube.com/channel/%s' % channel_id 
    channel_home = subprocess.run(['wget', '-q', '-O', '-', channel_url], capture_output=True, text=True).stdout
    avatar_url = re.search(r'"avatar":\{"thumbnails":\[\{"url":"(?P<img_url>[^"]+)"', channel_home).groupdict().get('img_url')
    # TODO: produce an error
    if avatar_url is None:
        pass
    else:
        subprocess.run(['wget', '-q', '-O', output_file, avatar_url])

def getAvatars(channels, output_file = 'avatar.jpg', batch_size = 10):

    ps0 = dict()

    # TODO: use batch_size

    # fire off wgets, first round
    for c in channels:
        dest_jpg = '../channels/%s/%s' % (c['id'], output_file)
        sys.stdout.write('getting avatar url for %s' % c['id'])
        if os.path.isfile(dest_jpg):
            print(' skipping')
            continue
        channel_url = 'https://www.youtube.com/channel/%s' % c['id']
        ps0[c['id']] = subprocess.Popen(['wget', '-q', '-O', '-', channel_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.stdout.write('\n')

    ps1= dict()

    # fire off wgets, second round
    for c_id, p in ps0.items():
        sys.stdout.write('downloading avatar for %s' % c_id)
        out, err = p.communicate()
        channel_home = out.decode()
        avatar_url = re.search(r'"avatar":\{"thumbnails":\[\{"url":"(?P<img_url>[^"]+)"', channel_home).groupdict().get('img_url')
        if avatar_url is None:
            sys.stderr.write(' ERR: could not find avatar URL\n')
            continue
        dest_jpg = '../channels/%s/%s' % (c_id, output_file)
        ps1[c_id] = subprocess.Popen(['wget', '-q', '-O', dest_jpg, avatar_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.stdout.write('\n')

    # wait for wgets to finish
    for c_id, p in ps1.items():
        out, err = p.communicate()
        print('avatar for %s done' % c_id)

def getThumbnails(videos, replace_existing = False):

    ps0 = dict()
    ps1 = dict()

    # fire off youtube-dls
    for v in videos:
        dest_jpg = '../channels/%s/thumbnails/%s.jpg' % (v['channel'], v['url'])
        sys.stdout.write('getting thumbnail url for %s' % v['url'])
        if os.path.isfile(dest_jpg) and not replace_existing:
            print(' skipping')
            continue
        os.makedirs('../channels/%s' % v['channel'], exist_ok=True)
        os.makedirs('../channels/%s/thumbnails' % v['channel'], exist_ok=True)

        print("CMD: " + ' '.join(['youtube-dl', '--list-thumbnails', 'https://www.youtube.com/watch?v=%s' % v['url']]))

        ps0[v['channel'] + ':' + v['url']] = subprocess.Popen(['youtube-dl', '--list-thumbnails', 'https://www.youtube.com/watch?v=%s' % v['url']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.stdout.write('\n')

    # fire off wgets
    for v_channel_url, p in ps0.items():
        v_channel = v_channel_url.split(':')[0]
        v_url = v_channel_url.split(':')[1]
        sys.stdout.write('downloading thumbnail for %s' % v_url)
        out, err = ps0[v_channel_url].communicate()
        lines = out.decode().split('\n')
        print("THUMBNAILS:")
        print(lines)
        print("END OF THUMBNAILS")
        first_thumbnail = next(line for line in lines if re.match(r'^\d+\s+\d+\s+\d+\s+.*', line))
        thumbnail_url = re.sub(r'\?.*', '', re.split(r'\s+', first_thumbnail)[-1])
        ps1[v_url] = subprocess.Popen(['wget', '-q', '-O', '../channels/%s/thumbnails/%s.jpg' % (v_channel, v_url), thumbnail_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.stdout.write('\n')

    # wait for wgets to finish
    for v_url, p in ps1.items():
        out, err = ps1[v_url].communicate()
        print('thumbnail for %s done' % v_url)


def fetchBacklog(channels, skip_existing = True, get_thumbnails = False, show_thumbnails = True, make_index = True, replace_json = True, max_vids_per_channel = None):

    for c in channels:

        dest_file = '../channels/%s/videos.json' % c['id']
        json_exists = os.path.isfile(dest_file)

        sys.stdout.write('channel: %s (%s)' % (c['id'], c['title']))
        sys.stdout.flush()

        os.makedirs('../channels/%s' % c['id'], exist_ok=True)

        if json_exists and skip_existing:
            sys.stdout.write(' skipping\n')
            continue

        playlist = 'UU' + c['id'][2:]

        if replace_json or not json_exists:
            result = subprocess.run(['youtube-dl', 'https://www.youtube.com/playlist?list=%s' % playlist, '--flat-playlist', '--dump-single-json'], capture_output=True, text=True)

            json_text = result.stdout.replace('},', '},\n')

            with open(dest_file, 'w') as fh:
                fh.write(json_text)
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
        <h1>""" + c['title'] + """</h1>
        <ul>
    """

                all_videos = json.loads(json_text)['entries']
                for v in all_videos:
                    v['channel'] = c['id']

                if max_vids_per_channel is None:
                    videos = all_videos
                else:
                    videos = all_videos[0:max_vids_per_channel]

                if get_thumbnails:
                    getThumbnails(videos)

                for v in videos:

                    if show_thumbnails:
                        if os.path.isfile('../channels/%s/thumbnails/%s.jpg' % (c['id'], v['url'])):
                            output += '<li><figure><a href="https://www.youtube.com/watch?v=%s"><img class="thumbnail" src="thumbnails/%s.jpg"></a><figcaption>%s</figcaption></figure></li>\n' % (v['url'], v['url'], v['title'])
                        else:
                            output += '<li><figure><a href="https://www.youtube.com/watch?v=%s">[no thumbnail]</a><figcaption>%s</figcaption></figure></li>\n' % (v['url'], v['title'])
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
    fetchBacklog(channels, skip_existing=False, get_thumbnails=False, make_index=True, replace_json = False, max_vids_per_channel=None)

if __name__ == "__main__":
    main()
