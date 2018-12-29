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

QIITA_ACCESS_TOKEN = os.environ["QIITA_ACCESS_TOKEN"]
QIITA_GET_API_URL = "https://qiita.com/api/v2/items/"
QIITA_HEADERS = {
    "Authorization": "Bearer 18465239840fcf5bc4be148777637e0ac9439893",
    "cache-control": "no-cache"
}
QIITA_HOST = "https://qiita.com"
QIITA_LIKES_THRESHOLD = 100

def get_likes(item_id):
    qiita_item_url = QIITA_GET_API_URL + item_id
    res = requests.request("GET", qiita_item_url, headers=QIITA_HEADERS)
    res.raise_for_status()
    res_json = res.json()
    return res_json["likes_count"]


def select_qiita():
    try:
        payload = {
            "consumer_key": POCKET_CONSUMER_KEY,
            "access_token": POCKET_ACCESS_TOKEN,
            "tag"         : "twitter",
            "detailType"  : "complete",
            "count"       : 500
        }
        res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=POCKET_HEADERS)
        res.raise_for_status()
        res_json = res.json()

        actions = []

        for item_id in res_json["list"].keys():
            if "resolved_id" not in res_json["list"][item_id].keys():
                continue

            if not res_json["list"][item_id]["resolved_id"].startswith(QIITA_HOST):
                continue

            qiita_item_id = res_json["list"][item_id]["resolved_id"].split("/")[-1]
            qiita_item_likes = get_likes(qiita_item_id)
            if qiita_item_likes >= QIITA_LIKES_THRESHOLD:
                action = {
                    "action" : "tags_remove",
                    "item_id": item_id,
                    "tags"   : "twitter"
                }
                action = {
                    "action" : "tags_add",
                    "item_id": item_id,
                    "tags"   : "selected_qiita"
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

        text  = "Success! %d items were selected." % (len(actions) / 2)
        color = "good"
    except:
        text  = "Failed!"
        color = "#ff0000"

    return { "text": text, "color": color }


def lambda_handler(event, context):
    token = os.environ["SLACK_OUTGOING_WEBHOOK_TOKEN"]
    query = parse_qs(event.get("body") or "")
    if query.get("token", [""])[0] != token:
        return { "statusCode": 400 }

    content = select_qiita()
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
