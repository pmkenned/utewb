#!/usr/bin/env python3
import subprocess
import xml.etree.ElementTree as ET
import json
import re
import sys

def updateFeeds(channels, verbose=False):

    ps = dict()

    for c in channels:
        if verbose:
            sys.stdout.write('getting feed for channel %s (%s)\n' % (c['id'], c['title']))
        rss = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % c['id']
        ps[c['id']] = subprocess.Popen(['wget', '-q', '-O', '-', rss], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    entries = []
    for c_id, p in ps.items():
        out, err = p.communicate()
        out = out.decode()
        with open('../channels/%s/feed.xml' % c_id, 'w') as fh:
            fh.write(out)
        if verbose:
            sys.stdout.write('got feed for channel %s)\n' % c_id)


def listRecentVideos(channels, update_feeds = True):

    if update_feeds:
        print('updating feeds...')
        updateFeeds()
        print('done')

    entries = []
    for c in channels:
        # TODO: handle if file is missing
        tree = ET.parse('../channels/%s/feed.xml' % c['id'])
        root = tree.getroot()
        for c0 in root:
            if c0.tag.endswith('entry'):
                e = dict()
                for c1 in c0:
                    if c1.tag.endswith('id'):
                        _id = json.dumps(c1.text)
                        gd = re.search(r'"yt:video:(?P<url>.*)"', _id).groupdict()
                        e['url'] = gd['url']
                    elif c1.tag.endswith('title'):
                        e['title'] = json.dumps(c1.text)
                    elif c1.tag.endswith('published'):
                        published = json.dumps(c1.text)
                        gd = re.search(r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)', published).groupdict()
                        e['published'] = '%s-%s-%s' % (gd['year'], gd['month'], gd['day'])
                entries.append(e)

    for e in entries:
        gd = re.search(r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)', e['published']).groupdict()
        (year, month, day) = (int(gd['year'],10), int(gd['month'],10), int(gd['day'],10))
        if year == 2021 and month == 6 and day == 6:
            print(e['title'])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('usage: %s [FILE]\n' % sys.argv[0])
        exit(1)
    channels = json.loads(open(sys.argv[1]).read())['channels']
    listRecentVideos(channels, update_feeds=False)
