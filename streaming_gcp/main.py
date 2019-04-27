#!/usr/bin/env python
# encoding: utf-8

import json
import os
import logging
from datetime import datetime, timedelta, timezone
import random
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s- %(name)s- %(message)s")

SLACK_POST_URL = os.getenv("SLACK_POST_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

POCKET_CONSUMER_KEY = os.getenv("POCKET_CONSUMER_KEY")
POCKET_ACCESS_TOKEN = os.getenv("POCKET_ACCESS_TOKEN")
POCKET_GET_API_URL = "https://getpocket.com/v3/get"
POCKET_HEADERS = {
    "content-type": "application/json;charset = UTF8",
    "x-accept": "application/json",
    "cache-control": "no-cache"
}


RANDOM255 = lambda: random.randint(0, 255)
JST = timezone(timedelta(hours=+9), 'JST')


def get_new_items():
    since_time = datetime.now(JST) - timedelta(minutes=1)
    since_unix_time = since_time.timestamp()
    payload = {
        "consumer_key": POCKET_CONSUMER_KEY,
        "access_token": POCKET_ACCESS_TOKEN,
        "sort": "newest",
        "detailType": "complete",
        "count": 10,
        "since": since_unix_time
    }

    res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
    res.raise_for_status()
    res_json = res.json()
    if isinstance(res_json["list"], list):
        return []

    contents = []
    for item_id in res_json["list"].keys():
        item_keys = res_json["list"][item_id].keys()
        in_item_keys = lambda x: x in item_keys
        if not all(map(in_item_keys, ("given_title", "given_url", "time_added"))):
            continue

        time_added = res_json["list"][item_id]["time_added"]
        if float(time_added) < since_unix_time:
            continue

        item_title = res_json["list"][item_id]["given_title"]
        item_url = res_json["list"][item_id]["given_url"]
        color_code = "#%02X%02X%02X" % (RANDOM255(), RANDOM255(), RANDOM255())

        content = {
            "fallback": "%s(%s)" % (item_title, item_url),
            "color": color_code,
            "fields": [
                {
                    "title": item_title,
                    "value": item_url
                }
            ],
            "ts": time_added
        }
        contents.append(content)

    return contents


def pocket_endpoint(data, context):
    try:
        contents = get_new_items()
        print(contents)
        if not contents:
            return

        slack_message = {
            "channel": SLACK_CHANNEL,
            "attachments": contents
        }

        res = requests.request("POST", SLACK_POST_URL, data=json.dumps(slack_message))
        res.raise_for_status()
        logger.info("Message posted to %s", slack_message["channel"])
        return
    except Exception as e:
        logger.error("Error: %s", e)
        return


if __name__ == '__main__':
    pocket_endpoint('a', 'b')
