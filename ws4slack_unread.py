import json
import requests
from time import sleep
from subprocess import call
from ws4py.client.threadedclient import WebSocketClient

TOKEN = ""
G9LED_PATH = "/home/papes1ns/Projects/g9led"
COLORS = {"on": "FFFFFF",
          "off": "000000"}


class SlackWebSocket(WebSocketClient):
    def __init__(self, *args, **kwargs):
        # SlackWebSocket will not create object if this request fails
        r = requests.post("https://slack.com/api/rtm.start", {'token': TOKEN}).json()

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
        while True:
            if len(self.unreads) > 0:
                if is_on != True:
                    call(G9LED_PATH + " %s" % COLORS['on'], shell=True)
                    is_on = True
            else:
                if is_on != False:
                    call(G9LED_PATH + " %s" % COLORS['off'], shell=True)
                    is_on = False
            sleep(1)


if __name__ == '__main__':
    try:
        ws = SlackWebSocket()
        ws.connect()
        ws.spawn_unread_checker()
    except KeyboardInterrupt:
        print "closing socket\n"
        ws.close()
