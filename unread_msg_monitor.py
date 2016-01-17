""" Program that changes the LED color of Logitech G9 mouse based on slack
unread message count. If there's unread messages, change LED to white, if
there's no message, simply turn off the light.

This program relies on the g9led executable, can be downloaded at:
  http://als.regnet.cz/logitech-g9-linux-led-color.html

Once g9led is downloaded and compiled, find a home for it and specify it's location in G9LED variable.
g9led requires sudo to successfully change LED color, so run script like:
  sudo python unread_msg_monitor.py

Generate your token at https://api.slack.com/web and add it to TOKEN variable.

To enable this program on start up, add the something like the following to /etc/rc.local:
  . /home/papes1ns/.virtualenvs/unread/bin/activate && python /home/papes1ns/Projects/hes_slack_integration/unread_msg_monitor.py &

Be sure to include the "." in the above command to source the enviroment.
"""

import requests
import sys
from subprocess import call
from time import sleep

SLACK_API_URL = "https://slack.com/api/"  # don't change
TOKEN = ""  # token can be generated at https://api.slack.com/web
G9LED_PATH = "/home/papes1ns/Projects/"  # where did you put g9led executable?

# has_unread G9 mouse color mapping
# can use any hex value for color
COLORS = {"True": "FFFFFF",  # white
          "False": "000000"}  # no light


def start_service():
    while True:
        has_unread = False

        try:
            # check for unread instant messages
            r = requests.post(SLACK_API_URL+"im.list", {"token": TOKEN})
            im_channels = [c.get("id", None) for c in r.json().get("ims", [])]
            for channel_id in im_channels:
                if channel_id is not None:
                    r = requests.post(SLACK_API_URL+"im.history", {"token": TOKEN,
                                                                   "channel": channel_id,
                                                                   "unreads": 1})
                    if r.json().get("unread_count_display", 0) > 0:
                        has_unread = True

            # check for unread channel posts
            r = requests.post(SLACK_API_URL+"channels.list", {"token": TOKEN})
            channels = [c.get("id", None) for c in r.json().get("channels", [])]
            for channel_id in channels:
                if channel_id is not None:
                    r = requests.post(SLACK_API_URL+"channels.history", {"token": TOKEN,
                                                                         "channel": channel_id,
                                                                         "unreads": 1})
                    if r.json().get("unread_count_display", 0) > 0:
                        has_unread = True

        except requests.exceptions.ConnectionError:
            sys.stderr.write("Could not connect to slack.\n")

        call(G9LED_PATH + "g9led " + COLORS[str(has_unread)], shell=True)
        sleep(1)  # let slack server rest for a second.. literally

if __name__ == "__main__":
    start_service()
