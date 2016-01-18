""" Program that changes the LED color of Logitech G9 mouse based on slack
unread message count. If there's unread messages, change LED to white, if
there's no message, turn off the light. Checks all IMS and channels subscribed.

This program relies on the g9led executable, can be downloaded at:
  http://als.regnet.cz/logitech-g9-linux-led-color.html

Once g9led is downloaded and compiled, find a home for it and specify it's
location in G9LED variable.

g9led requires sudo to successfully change LED color, so run script like:
  sudo python unread_msg_monitor.py

Generate your token at https://api.slack.com/web and add it to TOKEN variable.

To enable this program on start up, add the something like in /etc/rc.local:
  . /home/papes1ns/.virtualenvs/unread/bin/activate &&
  python /home/papes1ns/Projects/hes_slack_integration/unread_msg_monitor.py &

With 5 sec refresh rate, best case ~14 requests in 1 minute,
worst case ~113 requests in 1 minute.
"""

import requests
import sys
from os.path import isfile
from subprocess import call
from time import sleep

# user defined settings
TOKEN = ""
G9LED_PATH = "/home/papes1ns/Projects/g9led"  # where did you put g9led?
REFRESH_RATE = 5  # sleep for how many seconds between requests?

# has_unread G9 mouse color mapping
# can use any hex value for color
COLORS = {"True": "FFFFFF",  # white
          "False": "000000"}  # no light

# keys are slack api methods, values are keys to extract the data wanted
# https://api.slack.com/methods
API_METHODS = {
    "im.list": {
        "key": "ims",
        "history": "im.history"
    },
    "channels.list": {
        "key": "channels",
        "history": "channels.history"
    }
}

SLACK_API_URL = "https://slack.com/api/"


def update_led(has_unread):
    # has_unread: bool
    call(G9LED_PATH + " %s" % COLORS[str(has_unread)], shell=True)


def get_channel_ids(method, kwargs):
    # method: string
    # kwargs: dict

    try:
        r = requests.post(SLACK_API_URL + method, {"token": TOKEN})
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Could not connect to slack.\n")
        return []
    return [c.get("id", None) for c in r.json().get(kwargs["key"], [])]


def has_unread(channel_ids, kwargs, unread_id):
    # method: string
    # kwargs: dict
    # unread_id: sting

    if unread_id is not None:
        channel_ids = [unread_id]

    for channel_id in channel_ids:
        payload = {"token": TOKEN,
                   "channel": channel_id,
                   "unreads": 1}
        try:
            r = requests.post(SLACK_API_URL + kwargs["history"], payload)
        except requests.exceptions.ConnectionError:
            sys.stderr.write("Could not connect to slack.\n")

        if r.json().get("unread_count_display", 0) > 0:
            return channel_id
    return None


def start_service():
    channel_ids = []
    half_chans = True
    unread_id = None  # cache last unread channel id to be efficient
    while True:
        for method, kwargs in API_METHODS.iteritems():
            # get all im and normal channels once to be efficient
            if not channel_ids:
                channel_ids = get_channel_ids(method, kwargs)
            elif half_chans:
                channel_ids.append(get_channel_ids(method, kwargs))
                half_chans = False

            unread_id = has_unread(channel_ids, kwargs, unread_id)
            if unread_id:
                break  # avoid LED flicker and avoid unneeded POST to slack

        update_led(bool(unread_id))
        sleep(REFRESH_RATE)  # allow slack server to rest


if __name__ == "__main__":
    if not isfile(G9LED_PATH):
        sys.stderr.write("Could not find g9led executable in %s\n" % G9LED_PATH)
        sys.exit(1)

    if not TOKEN:
        sys.stderr.write("Please generate a token at https://api.slack.com/web " \
                          "and set the TOKEN value in the python script.\n")
        sys.exit(1)

    start_service()
