#!/usr/bin/env python
# encoding: utf-8

import json
import os
import logging
import random
from urllib.parse import parse_qs

import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s- %(name)s- %(message)s")

SLACK_POST_URL = os.environ["SLACK_POST_URL"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

POCKET_CONSUMER_KEY = os.environ["POCKET_CONSUMER_KEY"]
POCKET_ACCESS_TOKEN = os.environ["POCKET_ACCESS_TOKEN"]
POCKET_ARTICLE_BASE_URL = "https://getpocket.com/a/read/%s"
POCKET_GET_API_URL = "https://getpocket.com/v3/get"
POCKET_HEADERS = {
    "content-type": "application/json;charset = UTF8",
    "x-accept": "application/json",
    "cache-control": "no-cache"
}

NOT_INCLUDE_TAGS = [
    "amazon_dash_button",
    "conference",
    "done",
    "tool",
    "twitter"
]

RANDOM255 = lambda: random.randint(0,255)


def pick_up_item():
    payload = {
        "consumer_key": POCKET_CONSUMER_KEY,
        "access_token": POCKET_ACCESS_TOKEN,
        "tag": NOT_INCLUDE_TAGS,
        "sort": "oldest",
        "count": 5000
    }

    res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
    res.raise_for_status()
    res_json = res.json()

    item_ids = list(res_json["list"].keys())
    item_id = random.choice(item_ids)

    item_title = res_json["list"][item_id]["resolved_title"]
    item_url = POCKET_ARTICLE_BASE_URL % res_json["list"][item_id]["item_id"]
    time_added = res_json["list"][item_id]["time_added"]
    color_code = "#%02X%02X%02X" % (RANDOM255(), RANDOM255(), RANDOM255())

    content = {
        "fallback": item_title,
        "color": color_code,
        "fields":[
            {
            "title": item_title,
            "value": item_url
            }
        ],
        "ts": time_added
    }

    return content


def lambda_handler(event, context):
    try:
        content = pick_up_item()

        slack_message = {
            "channel"    : SLACK_CHANNEL,
            "attachments": [
                content
            ],
        }

        res = requests.request("POST", SLACK_POST_URL, data=json.dumps(slack_message))
        res.raise_for_status()
        logger.info("Message posted to %s", slack_message["channel"])
        return {"statusCode": 200}
    except Exception as e:
        logger.error("Error: %s", e)
        return {"statusCode": 400}
