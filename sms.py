import requests
import time
import os
import logging

ENDPOINT = os.getenv("ENDPOINT")


def send_sms(phone_number, message):
    response = requests.post(
        url=ENDPOINT + "/goform/goform_set_cmd_process",
        headers={"Referer": ENDPOINT + "/index.html"},
        data={
            "goformId": "SEND_SMS",
            "Number": phone_number,
            "MessageBody": message.encode("utf-16be").hex().upper(),
            "ID": "-1",
            "encode_type": "GSM7_default",
        },
    )
    return response.json()


def get_sms(tag):
    response = requests.get(
        url=ENDPOINT + "/goform/goform_get_cmd_process",
        headers={"Referer": ENDPOINT + "/index.html"},
        params={
            "cmd": "sms_data_total",
            "page": "0",
            "data_per_page": "500",
            "mem_store": "1",
            "tags": tag,
            "order_by": "order by id desc",
        },
    )
    data = response.json()
    for sms in data["messages"]:
        sms["content"] = bytes.fromhex(sms["content"]).decode("utf-16be")
    return data


def get_all_sms():
    return get_sms("10")


def get_unread_sms():
    return get_sms("1")


def set_sms_tag(sms_id, tag):
    response = requests.post(
        url=ENDPOINT + "/goform/goform_set_cmd_process",
        headers={"Referer": ENDPOINT + "/index.html"},
        data={
            "goformId": "SET_MSG_READ",
            "msg_id": f"{sms_id};",
            "tag": tag,
        },
    )
    return response.json()


def set_sms_read(sms_id):
    return set_sms_tag(sms_id, "0")


def set_sms_unread(sms_id):
    return set_sms_tag(sms_id, "1")


def delete_sms(sms_id):
    response = requests.post(
        url=ENDPOINT + "/goform/goform_set_cmd_process",
        headers={"Referer": ENDPOINT + "/index.html"},
        data={
            "goformId": "DELETE_SMS",
            "msg_id": f"{sms_id};",
        },
    )
    return response.json()


def poll_sms(callback=lambda sms: print(sms), interval=5):
    while True:
        data = get_unread_sms()
        if data["messages"]:
            for sms in data["messages"]:
                if not callback(sms):
                    logging.error("Failed to process SMS")
                else:
                    set_sms_read(sms["id"])
        time.sleep(interval)
