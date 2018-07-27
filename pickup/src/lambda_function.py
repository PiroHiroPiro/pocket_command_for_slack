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
logging.basicConfig(format='%(asctime)s- %(name)s- %(message)s')

SLACK_POST_URL = os.environ['SLACK_POST_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
POCKET_CONSUMER_KEY = os.environ['POCKET_CONSUMER_KEY']
POCKET_ACCESS_TOKEN = os.environ['POCKET_ACCESS_TOKEN']

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
                "tool",
                "twitter"
            ],
            "sort": "oldest",
            "count": 250
        }
        res = requests.request("POST", POCKET_GET_API_URL, data=json.dumps(payload), headers=HEADERS)
        res.raise_for_status()
        res_json = res.json()
        items = list(res_json['list'].keys())
        item_id = random.choice(items)
        text = "%s (%s)" % (res_json['list'][item_id]['resolved_title'], res_json['list'][item_id]['resolved_url'])
        color = "good"
    except:
        text = "Failed!"
        color = "#ff0000"
    return { "text": text, "color": color }

def lambda_handler(event, context):
    token = os.environ['SLACK_OUTGOING_WEBHOOK_TOKEN']
    query = parse_qs(event.get('body') or '')
    if query.get('token', [''])[0] != token:
        return { 'statusCode': 400 }
    slackbot_name = 'pocketer'
    if query.get('user_name', [slackbot_name])[0] == slackbot_name:
        return { 'statusCode': 200 }
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
        return { 'statusCode': 200 }
    except requests.exceptions.RequestException as e:
        logger.error('Request failed: %s', e)
        return { 'statusCode': 400 }
