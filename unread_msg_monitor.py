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
"""

import requests
import sys
import os
from subprocess import call
from time import sleep

# user defined settings
TOKEN = ""
G9LED_PATH = "/home/papes1ns/Projects/g9led"  # where did you put g9led executable?

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


def start_service():
    while True:
        has_unread = False
        for method, kwargs in API_METHODS.iteritems():
            try:
                r = requests.post(SLACK_API_URL + method, {"token": TOKEN})
                im_channels = [c.get("id", None) for c in r.json().get(kwargs["key"], [])]
                for channel_id in im_channels:
                    payload = {"token": TOKEN,
                               "channel": channel_id,
                               "unreads": 1}
                    r = requests.post(SLACK_API_URL + kwargs["history"], payload)
                    if r.json().get("unread_count_display", 0) > 0:
                        has_unread = True

            except requests.exceptions.ConnectionError:
                sys.stderr.write("Could not connect to slack.\n")

        call(G9LED_PATH + " " + COLORS[str(has_unread)], shell=True)
        sleep(1)  # let slack server rest for a second.. literally

if __name__ == "__main__":
    if not os.path.isfile(G9LED_PATH):
        sys.stderr.write("Could not find g9led executable in %s\n" % G9LED_PATH)
        sys.exit(1)

    if not TOKEN:
        sys.stderr.write("Please generate a token at https://api.slack.com/web " \
                          "and set the TOKEN value in the python script.\n")
        sys.exit(1)

    start_service()
