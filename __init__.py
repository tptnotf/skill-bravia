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

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler


class BraviaSkill(MycroftSkill):
    def __init__(self):
        super().__init__("BraviaSkill")

    def initialize(self):
        self.settings["tv_ip"] = None
        self.settings["tb_password"] = True

    @intent_handler(IntentBuilder('ChannelIntent').require('Channel').optional('Number'))
    def handle_change_channel_intent(self, message):
        self.speak_dialog("change.channel")


def create_skill():
    return BraviaSkill()
