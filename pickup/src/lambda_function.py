#!/usr/bin/env python
# encoding: utf-8

import json
import requests
import os
import logging
import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s- %(name)s- %(message)s')

SLACK_POST_URL = os.environ['SLACK_POST_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
POCKET_CONSUMER_KEY = os.environ['POCKET_CONSUMER_KEY']
POCKET_ACCESS_TOKEN = os.environ['POCKET_ACCESS_TOKEN']
POCKET_ARTICLE_BASE_URL = 'https://getpocket.com/a/read/%s'

POCKET_GET_API_URL = "https://getpocket.com/v3/get"
HEADERS = {
    'content-type': "application/json;charset = UTF8",
    'x-accept': "application/json",
    'cache-control': "no-cache"
}


def pick_up():
    try:
        payload = {
            "consumer_key": POCKET_CONSUMER_KEY,
            "access_token": POCKET_ACCESS_TOKEN,
            "tag": [
                "amazon_dash_button",
                "conference",
                "done",
                "english",
                "tool",
                "twitter"
            ],
            "sort": "oldest",
            "count": 5000
        }
        res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=HEADERS)
        res.raise_for_status()
        res_json = res.json()
        items = list(res_json['list'].keys())
        item_id = random.choice(items)
        text = "%s (%s)" % (res_json['list'][item_id]['resolved_title'], POCKET_ARTICLE_BASE_URL % res_json['list'][item_id]['item_id'])
        color = "good"
    except:
        text = "Failed!"
        color = "#ff0000"
    return {"text": text, "color": color}


def lambda_handler(event, context):
    content = pick_up()
    slack_message = {
        'channel'    : SLACK_CHANNEL,
        'attachments': [
            content
        ],
    }
    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info('Message posted to %s', slack_message['channel'])
        return {'statusCode': 200}
    except requests.exceptions.RequestException as e:
        logger.error('Request failed: %s', e)
        return {'statusCode': 400}
