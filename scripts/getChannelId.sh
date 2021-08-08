#!/usr/bin/env bash

# const a_tags = document.getElementsByTagName("a");
# const channels = [].filter.call(document.getElementsByClassName('ytd-grid-channel-renderer'), el => el.nodeName == "A");
# channels.forEach((x) => {console.log(x.href, x.text);});

username='schafer5'

curl 'https://socialnewsify.com/wp-admin/admin-ajax.php' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'X-Requested-With: XMLHttpRequest' -H 'Origin: https://socialnewsify.com' -H 'Connection: keep-alive' -H 'Referer: https://socialnewsify.com/get-channel-id-by-username-youtube/' --data-raw "action=getChannelID&username=${username}"
