# slack_unread_msg_monitor
Program that changes the LED color of Logitech G9 mouse based on slack unread message count. If there's unread messages, change LED to white, if there's no message, simply turn off the light.

# Setup
This program relies on the g9led executable, can be downloaded at:
http://als.regnet.cz/logitech-g9-linux-led-color.html

Once g9led is downloaded and compiled, find a home for it and specify it's location in G9LED variable.
g9led requires sudo to successfully change LED color, so run script like: `sudo python ws4slack_unread.py`

Generate your token at https://api.slack.com/web and add it to TOKEN variable.

Requires `ws4py` and `requests`, you can install them with pip.

To enable this program on start up, add the something like the following to /etc/rc.local:
`. /home/papes1ns/.virtualenvs/unread/bin/activate && python /home/papes1ns/Projects/hes_slack_integration/ws4slack_unread.py &`
