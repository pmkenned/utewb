#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import xml.etree.ElementTree as ET
import json
import pprint as pp

# see:
# https://www.tutorialkart.com/python/python-xml-parsing/
# https://docs.python.org/3/library/http.server.html
# https://blog.anvileight.com/posts/simple-python-http-server/
# https://waylonwalker.com/parsing-rss-python/
# https://socialnewsify.com/get-channel-id-by-username-youtube/

rss = 'https://www.youtube.com/feeds/videos.xml?channel_id=UC6qj_bPq6tQ6hLwOBpBQ42Q'
rss = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCYO_jab_esuFRV4b17AJtAw'

channels = [
#    'https://www.youtube.com/c/3blue1brown/',
#    'https://www.youtube.com/channel/UC6qj_bPq6tQ6hLwOBpBQ42Q',
    'https://www.youtube.com/channel/UCEmuohuDgJtmmeOCUI3DOQg/'
]


index = br"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>utewb</title>
    </head>
    <body>

        <button onclick="f()">B1</button>

        <script>
function f() {
    fetch('/foo')
        .then(response => response.json())
        .then(data => console.log(data));
}
        </script>

    </body>
</html>"""


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        resp = None

        if self.path == '/':
            resp = index
        elif self.path == '/foo':

            #result = subprocess.run(['youtube-dl', '--dateafter', '20210101', '--get-filename', '-o' '"%(upload_date)s, %(title)s, https://www.youtube.com/watch?v=%(id)s"', channel], capture_output=True, text=True)

            result = subprocess.run(['wget', '-O', '-', rss], capture_output=True, text=True)

            root = ET.fromstring(result.stdout)

            titles = []
            for c in root:
                if 'entry' in c.tag:
                    for c2 in c:
                        if 'title' in c2.tag:
                            titles.append(json.dumps(c2.text))
            resp_str = '{"titles": [' + ','.join(titles) + ']}'
            #print(resp_str)
            resp = bytes(resp_str, 'utf-8')
        else:
            resp = b'?'

        self.send_response(200)
        self.end_headers()
        self.wfile.write(resp)


def main():
    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
