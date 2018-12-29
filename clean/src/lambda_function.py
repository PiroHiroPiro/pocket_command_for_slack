#!/usr/bin/env python
# encoding: utf-8

import json
import requests
import os
import logging
from urllib.parse import parse_qs


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s- %(name)s- %(message)s")

SLACK_POST_URL = os.environ["SLACK_POST_URL"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

POCKET_CONSUMER_KEY = os.environ["POCKET_CONSUMER_KEY"]
POCKET_ACCESS_TOKEN = os.environ["POCKET_ACCESS_TOKEN"]
POCKET_GET_API_URL = "https://getpocket.com/v3/get"
POCKET_SEND_API_URL = "https://getpocket.com/v3/send"
POCKET_HEADERS = {
    "content-type": "application/json;charset = UTF8",
    "x-accept": "application/json",
    "cache-control": "no-cache"
}

TWITTER_HOST = "https://twitter.com/"


def clean_items():
    try:
        payload = {
            "consumer_key": POCKET_CONSUMER_KEY,
            "access_token": POCKET_ACCESS_TOKEN,
            "tag"         : "twitter",
            "detailType"  : "complete",
            "count"       : 5000
        }
        res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
        res.raise_for_status()
        res_json = res.json()
        actions = []

        for item_id in res_json["list"].keys():
            item_keys = res_json["list"][item_id].keys()
            in_item_keys = lambda x:x in item_keys
            if not all(map(in_item_keys, ("resolved_url", "tags"))):
                continue

            # TwitterへのURLを持つitemの削除
            if res_json["list"][item_id]["resolved_url"].startswith(TWITTER_HOST):
                action = {
                    "action" : "delete",
                    "item_id": item_id
                }
                actions.append(action)

            # "twitter"以外のtagも付与されているitemから"twitter"tagの削除
            if len(res_json["list"][item_id]["tags"]) >= 2:
                action = {
                    "action" : "tags_remove",
                    "item_id": item_id,
                    "tags"   : "twitter"
                }
                actions.append(action)

        if len(actions) > 0:
            payload = {
                "consumer_key": POCKET_CONSUMER_KEY,
                "access_token": POCKET_ACCESS_TOKEN,
                "actions"     : actions
            }
            res = requests.request("POST", POCKET_SEND_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
            res.raise_for_status()

        text = "Cleaned  %d items." % len(actions)
        color = "good"
    except:
        text = "Clean items failed!"
        color = "#ff0000"

    return { "text": text, "color": color }


def lambda_handler(event, context):
    token = os.environ["SLACK_OUTGOING_WEBHOOK_TOKEN"]
    query = parse_qs(event.get("body") or "")
    if query.get("token", [""])[0] != token:
        logger.error("Undefined token: %s", query.get("token", [""])[0])
        return { "statusCode": 400 }

    content = clean_items()
    slack_message = {
        "channel"    : SLACK_CHANNEL,
        "attachments": [
            content
        ],
    }

    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message["channel"])
        return { "statusCode": 200 }
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
        return { "statusCode": 400 }
