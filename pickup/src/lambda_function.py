#!/usr/bin/env python
# encoding: utf-8

import json
import requests
import os
import logging
import random
from urllib.parse import parse_qs


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

random_255 = lambda: random.randint(0,255)


def pick_up_item():
    try:
        not_include_tags = [
                "amazon_dash_button",
                "conference",
                "done",
                "tool",
                "twitter"
        ]
        payload = {
            "consumer_key": POCKET_CONSUMER_KEY,
            "access_token": POCKET_ACCESS_TOKEN,
            "tag": not_include_tags,
            "sort": "oldest",
            "count": 2000
        }

        res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
        res.raise_for_status()
        res_json = res.json()

        item_ids = list(res_json["list"].keys())
        item_id = random.choice(item_ids)

        item_title = res_json["list"][item_id]["resolved_title"]
        item_url = POCKET_ARTICLE_BASE_URL % res_json["list"][item_id]["item_id"]
        time_added = res_json["list"][item_id]["time_added"]
        color_code = "#%02X%02X%02X" % (random_255(),random_255(),random_255())

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

    except:
        content = {
            "text": "Pick up Failed!",
            "color": "danger"
        }

    return content


def lambda_handler(event, context):
    content = pick_up_item()
    slack_message = {
        "channel"    : SLACK_CHANNEL,
        "attachments": [
            content
        ],
    }

    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message["channel"])
        return {"statusCode": 200}
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
        return {"statusCode": 400}
