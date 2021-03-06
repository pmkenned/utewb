#!/usr/bin/env python3
import subprocess
import xml.etree.ElementTree as ET
import json
import re
import sys
import os
import datetime

# TODO: update backlogs with feed data
def fetchFeeds(channels, verbose=False, update_feeds = True):

    ps = dict()

    for c in channels:
        if verbose:
            sys.stdout.write('getting feed for channel %s (%s)...' % (c['id'], c['title']))
            sys.stdout.flush()
        if os.path.isfile('../channels/%s/feed.xml' % c['id']):
            if verbose:
                sys.stdout.write(' skipping\n')
            continue
        else:
            if verbose:
                sys.stdout.write('\n')
        rss = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % c['id']
        ps[c['id']] = subprocess.Popen(['wget', '-q', '-O', '-', rss], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for c_id, p in ps.items():
        out, err = p.communicate()
        out = out.decode()
        os.makedirs('../channels/%s' % c_id, exist_ok=True)
        with open('../channels/%s/feed.xml' % c_id, 'w') as fh:
            fh.write(out)
        if verbose:
            sys.stdout.write('got feed for channel %s)\n' % c_id)


def listRecentVideos(channels, update_feeds = True, from_days_ago = 5):

    recentUploads = []

    print('getting feeds...')
    fetchFeeds(channels, update_feeds=update_feeds)
    print('done getting feeds')

    entries = []
    for c in channels:
        # TODO: handle if file is missing
        tree = ET.parse('../channels/%s/feed.xml' % c['id'])
        root = tree.getroot()
        for c0 in root:
            if c0.tag.endswith('entry'):
                e = dict()
                e['channel'] = c['id']
                for c1 in c0:
                    if c1.tag.endswith('id'):
                        _id = json.dumps(c1.text)
                        gd = re.search(r'"yt:video:(?P<url>.*)"', _id).groupdict()
                        e['url'] = gd['url']
                    elif c1.tag.endswith('title'):
                        e['title'] = json.dumps(c1.text)[1:-1] # remove quotation marks
                    elif c1.tag.endswith('published'):
                        published = json.dumps(c1.text)
                        gd = re.search(r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)', published).groupdict()
                        e['published'] = '%s-%s-%s' % (gd['year'], gd['month'], gd['day'])
                entries.append(e)

    for e in entries:
        gd = re.search(r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)', e['published']).groupdict()
        vid_date = datetime.date(int(gd['year'],10), int(gd['month'],10), int(gd['day'],10))
        n_days_ago = (datetime.datetime.now() - datetime.timedelta(days=from_days_ago)).date()
        if vid_date > n_days_ago:
            recentUploads.append(e)

    return recentUploads


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('usage: %s [FILE]\n' % sys.argv[0])
        exit(1)
    channels = json.loads(open(sys.argv[1]).read())['channels']
    listRecentVideos(channels, update_feeds=False)
