#!/usr/bin/env python
# encoding: utf-8

import json
import requests
import os
import logging
from urllib.parse import parse_qs
from datetime import datetime, timedelta


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s- %(name)s- %(message)s")

SLACK_POST_URL = os.environ["SLACK_POST_URL"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

POCKET_CONSUMER_KEY = os.environ["POCKET_CONSUMER_KEY"]
POCKET_ACCESS_TOKEN = os.environ["POCKET_ACCESS_TOKEN"]
POCKET_GET_API_URL = "https://getpocket.com/v3/get"
POCKET_HEADERS = {
    "content-type": "application/json;charset = UTF8",
    "x-accept": "application/json",
    "cache-control": "no-cache"
}

not_include_tags = [
    "conference",
    "done",
    "tool",
    "twitter",
    "english",
    "favorite",
    "keep",
    "selected_qiita"
]


def get_new_item():
    from_time = datetime.now() -  timedelta(minutes=1)
    from_unix_time = from_time.timestamp()

    payload = {
        "consumer_key": POCKET_CONSUMER_KEY,
        "access_token": POCKET_ACCESS_TOKEN,
        "sort": "newest",
        "detailType"  : "complete",
        "count": 10,
        "since": from_unix_time
    }

    res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
    res.raise_for_status()
    res_json = res.json()

    if isinstance(res_json["list"], list):
        return

    for item_id in res_json["list"].keys():
        item_keys = res_json["list"][item_id].keys()
        in_item_keys = lambda x:x in item_keys
        if not all(map(in_item_keys, ("given_title", "given_url", "tags"))):
            continue

        item_tags = res_json["list"][item_id]["tags"].keys()
        in_item_tags = lambda x:x in item_tags
        if any(map(in_item_tags, not_include_tags)):
            continue

        item_title = res_json["list"][item_id]["given_title"]
        item_url = res_json["list"][item_id]["given_url"]
        updated_time = res_json["list"][item_id]["time_updated"]

        content = {
            "fallback": item_title,
            "pretext":"新規アイテムがPocketに登録されました",
            "fields":[
                {
                "title": item_title,
                "value": item_url
                }
            ],
            "color": "good",
            "ts": updated_time
        }

        send_item(content)

    return


def send_item(content):
    slack_message = {
        "channel"    : SLACK_CHANNEL,
        "attachments": [
            content
        ]
    }

    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message["channel"])
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)

    return


def lambda_handler(event, context):
    try:
        get_new_item()
        return {"statusCode": 200}
    except Exception as e:
        logger.error("Request failed: %s", e)
        return {"statusCode": 400}
