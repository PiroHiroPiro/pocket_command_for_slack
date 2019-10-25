#!/usr/bin/env python
# encoding: utf-8

import datetime
import json
import logging
import os

import boto3
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_POST_URL = os.environ["SLACK_POST_URL"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

response = boto3.client("cloudwatch", region_name="us-east-1")
last_date = (datetime.date.today() -datetime.timedelta(1)).strftime("%Y/%m/%d")
service_list = []
service_value = []


def floatFormat(n):
    try:
        return round(n * 100) / 100
    except:
        return n


def get_each_service_value(service_name):
    data = response.get_metric_statistics(
        Namespace = "AWS/Billing",
        MetricName = "EstimatedCharges",
        Period = 86400,
        StartTime = last_date + " 00:00:00",
        EndTime = last_date + " 23:59:59",
        Statistics = [
            "Maximum"
        ],
        Dimensions = [
            {
                "Name" : "ServiceName",
                "Value": service_name
            },
            {
                "Name" : "Currency",
                "Value": "USD"
            }
        ]
    )
    for info in data["Datapoints"]:
        return info["Maximum"]


def get_metric():
    get_metric_statistics = response.get_metric_statistics(
        Namespace = "AWS/Billing",
        MetricName = "EstimatedCharges",
        Dimensions = [
            {
                "Name": "Currency",
                "Value": "USD"
            }
        ],
        StartTime = datetime.datetime.today() - datetime.timedelta(days = 1),
        EndTime = datetime.datetime.today(),
        Period = 86400,
        Statistics = ["Maximum"])

    total_value = get_metric_statistics["Datapoints"][0]["Maximum"]

    json_value = response.list_metrics()
    for attr1 in json_value.get("Metrics"):
        for attr2 in attr1.get("Dimensions"):
            if attr2.get("Name") == "ServiceName":
                 service_list.append(attr2.get("Value"))
    for service in service_list:
        service_value.append(get_each_service_value(service))

    return total_value


def build_message():
    total_value = get_metric()
    if float(total_value) >= 10.0:
        color = "#ff0000"
    elif float(total_value) > 0.0:
        color = "warning"
    else:
        color = "good"
    attachment = {
        "pretext": "今月のAWSの利用費は…",
        "color"  : color,
        "fields" : []
    }
    total_item = {
        "title": "Total",
        "value": "$ " + str(floatFormat(total_value)) ,
        "short": "true"
    }
    attachment["fields"].append(total_item)
    for idx in range(len(service_list)):
        service_item = {
            "title": service_list[idx],
            "value": "$" + str(floatFormat(service_value[idx])),
            "short": "true"
        }
        attachment["fields"].append(service_item)
    return attachment


def lambda_handler(event, context):
    content = build_message()

    slack_message = {
        "channel"    : SLACK_CHANNEL,
        "attachments": [
            content
        ],
    }

    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message["channel"])
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
