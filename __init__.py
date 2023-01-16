# Copyright 2021, David Giral
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import requests

from ovos_utils.intents import IntentBuilder
from ovos_utils.parse import match_one, match_all, fuzzy_match
from ovos_workshop.skills import OVOSSkill
from mycroft import intent_handler
from ovos_utils.log import LOG
from lingua_franca import get_default_lang, load_language
from lingua_franca.parse import yes_or_no, extract_number

from .bravia_client import Client, ClientApp

class BraviaSkill(OVOSSkill):
    def __init__(self):
        super().__init__()
        self.clients = []
        self.vol_inc = 5

    def initialize(self):
        dc_ip = self.settings.get("dc_ip", None)
        if dc_ip and dc_ip.split(".")[-1].isdigit():
            self.clients.append(Client(self.settings.get("dc_name", ""), dc_ip, int(self.settings.get("dc_port", 5555)), self.settings.get("dc_key", "")))
        self._populate_clients()
        load_language(self.lang)
        self.vol_inc = self.settings.get("vol_increment", self.vol_inc)

#########################
#
# Power Management
#

    @intent_handler("turn.on.tv.intent")
    def handle_turn_on_tv_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            if not client.is_on:
                client.power_on()
                self.speak_dialog("turn.on.tv", {"name": client.name})
            else:
                self.speak_dialog('already.on', {'name': client.name})
        else:
            self.speak_dialog('no.client')

    @intent_handler("turn.off.tv.intent")
    def handle_turn_off_tv_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            if client.is_on:
                client.power_off()
                self.speak_dialog("turn.off.tv", {"name": client.name})
            else:
                self.speak_dialog('already.off', {'name': client.name})
        else:
            self.speak_dialog('no.client')

    @intent_handler("reboot.tv.intent")
    def handle_reboot_tv_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            if self.ask_yesno("are you sure you want to reboot"):
                self.speak_dialog("rebooting")
                client.request_reboot()
            else:
                self.speak_dialog("reboot canceled")

#
# End Power Management
#
############################

############################
#
# Sound Management
#

    @intent_handler("turn.up.tv.volume.intent")
    def handle_turn_up_tv_volume_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            LOG.info(f"active_client: {client.name}")
            client.volume = client.volume + self.vol_inc
            self.speak_dialog("tv.volume.up", {"name": client.name,
                                            "volume": client.volume})
        else:
            self.speak_dialog('no.client')

    @intent_handler("turn.up.tv.volume.amount.intent")
    def handle_turn_up_tv_volume_amount_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            amount = extract_number(message.data.get("amount", None))
            if amount:
                client.volume = client.volume + amount
                self.speak_dialog("tv.volume.set.to", {"name": client.name,
                                                       "volume": client.volume})
            else:
                self.handle_turn_up_tv_volume_intent(message)
        else:
            self.speak_dialog("no.client")

    @intent_handler("turn.down.tv.volume.intent")
    def handle_turn_down_tv_volume_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            LOG.info(f"active_client: {client.name}")
            client.volume = client.volume - self.vol_inc
            self.speak_dialog("tv.volume.down", {"name": client.name,
                                            "volume": client.volume})
        else:
            self.speak_dialog('no.client')

    @intent_handler("turn.down.tv.volume.amount.intent")
    def handle_turn_down_tv_volume_amount_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            amount = extract_number(message.data.get("amount", None))
            if amount:
                client.volume = client.volume - amount
                self.speak_dialog("tv.volume.set.to", {"name": client.name,
                                                       "volume": client.volume})
            else:
                self.handle_turn_down_tv_volume_intent(message)
        else:
            self.speak_dialog("no.client")

    @intent_handler("mute.tv.volume.intent")
    def handle_mute_tv_volume_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.mute()
            self.speak_dialog("mute.tv.volume", {"name": client_name})
        else:
            self.speak_dialog("no.client")

    @intent_handler("unmute.tv.volume.intent")
    def handle_unmute_tv_volume_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.unmute()
            self.speak_dialog("unmute.tv.volume", {"name": client_name})
        else:
            self.speak_dialog("no.client")

#
# End Sound Stuff
#
###############################

###############################
#
# App Stuff
#

    @intent_handler("open.tv.app.intent")
    def handle_open_tv_app_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            wanted_app = message.data.get("app_name", None)
            matches = []
            if wanted_app:
                LOG.debug(f"wanted app: {wanted_app}")
                for app in client.app_list:
                    if fuzzy_match(wanted_app, app['title']) >= .5:
                        matches.append(app)
                for app in matches:
                    if wanted_app.lower() in app['title'].lower():
                        wanted_app = app
                        break
                if not isinstance(wanted_app, dict) and len(matches) > 0:
                    wanted_app = matches[0] # pick the first in the list if all else fails
                    LOG.debug(f"wanted app in 'not isinstance': {wanted_app}")
                    client.set_active_app(wanted_app.uri)
                    self.speak_dialog("opened.tv.app", {"app_name": wanted_app.title,
                                                        "tv_name": client.name})
                else:

                    self.speak_dialog("no.app", {"app_name": wanted_app,
                                                 "tv_name": client.name})
        else:
            self.speak_dialog('no.client')

#
# End App Stuff
#
################################

################################
#
# Player Controls
#
# The Bravia REST API does not provide a direct way to get the playing status of all apps
# These functions mainly just emulate a remote button press
#

    @intent_handler("pause.player.intent")
    def handle_pause_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Pause")

    @intent_handler("play.player.intent")
    def handle_play_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Play")

    @intent_handler("stop.player.intent")
    def handle_stop_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Stop")

    @intent_handler("fast.forward.player.intent")
    def handle_fast_forward_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Forward")

    @intent_handler("rewind.player.intent")
    def handle_rewind_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Rewind")

    @intent_handler("next.player.intent")
    def handle_next_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Next")

    @intent_handler("last.player.intent")
    def handle_last_player_intent(self, message):
        if self.clients:
            client = self.get_client(message.data.get("name", None))
            client.send_command("Last")

################################
#
# Other Functions
#

    def get_client(self, client_name=None):
        if len(self.clients) >= 1:
            active_client = self.clients[0]
            for client in self.clients:
                if client_name == client.name:
                    active_client = client
        return active_client

    def _populate_clients(self):
        client_list = self.settings.get("clients", None)
        LOG.info(f"in _populate_clients:  {client_list}")
        if client_list:
            for client in client_list:
                LOG.info(client)
                self.clients.append(Client(client["name"], client["ip"], client["port"], client["access_key"]))

def create_skill():
    return BraviaSkill()

