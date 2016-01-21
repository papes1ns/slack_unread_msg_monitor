""" Program changes the LED color of Logitech G9 mouse based on slack
unread message count. If there's unread messages, change LED to white, if
there's no message, turn off the light. Checks all subscribed channels.

This program relies on the g9led executable, can be downloaded at:
  http://als.regnet.cz/logitech-g9-linux-led-color.html

Once g9led is downloaded and compiled, find a home for it and specify it's
location in G9LED variable.

Requires the python packages: ws4py and requests. Can be installed with pip.

g9led requires sudo to successfully change LED color, so run script like:
  sudo python ws4slack_unreadr.py

Generate your token at https://api.slack.com/web and add it to TOKEN variable.

To enable this program on start up, add the something like in /etc/rc.local:
  /home/papes1ns/.virtualenvs/unread/bin/python /home/papes1ns/Projects/slack_unread_msg_monitor/ws4slack_unread.py &
"""

import json
import requests
from time import sleep
from subprocess import call
from ws4py.client.threadedclient import WebSocketClient

TOKEN = ""  # slack token you generated goes here
G9LED_PATH = "/home/papes1ns/Projects/g9led"  # where did you put g9led?

# color mapping for unread (on) and read (off). Use any hex colors your heart desires
COLORS = {"on": "FFFFFF",
          "off": "000000"}


class SlackWebSocket(WebSocketClient):
    def __init__(self, *args, **kwargs):
        # SlackWebSocket will not create object if this request fails
        r = self.get_slack_ws_data()

        self.channels = []
        self.unreads = {}

        for channel_type in ['channels', 'mpims', 'ims', 'groups']:
            for c in r.get(channel_type, []):
                self.channels.append(c['id'])

        super(SlackWebSocket, self).__init__(r['url'])

    def received_message(self, m):
        data = json.loads(str(m))
        if data['type'] == 'message' and 'reply_to' not in data:
            if data['channel'] in self.channels:
                if data['channel'] in self.unreads:
                    self.unreads[data['channel']].append(data['text'])
                else:
                    self.unreads[data['channel']] = [data['text']]

        elif data['type'] in ['im_marked', 'channel_marked', 'group_marked', 'mpim_marked']:
            if data['channel'] in self.channels:
                del self.unreads[data['channel']]

    def spawn_unread_checker(self):
        is_on = False
        first_run = True
        while True:
            if len(self.unreads) > 0:
                if is_on is not True:
                    call(G9LED_PATH + " %s" % COLORS['on'], shell=True)
                    is_on = True
            else:
                if is_on is not False:
                    call(G9LED_PATH + " %s" % COLORS['off'], shell=True)
                    is_on = False
		elif first_run is True:
                    call(G9LED_PATH + " %s" % COLORS['off'], shell=True)
		    first_run = False
            sleep(1)

    def get_slack_ws_data(self):
        while True:
            try:
                r = requests.post("https://slack.com/api/rtm.start", {'token': TOKEN})
                return r.json()
            except requests.exceptions.ConnectionError as e:
                with open("/home/papes1ns/logs/ws4slack_unread.log", "a+") as out:
                    out.write(str(e) + "\n")
                sleep(5)



if __name__ == '__main__':
    try:
        ws = SlackWebSocket()
        ws.connect()
        ws.spawn_unread_checker()
    except KeyboardInterrupt:
        ws.close()
