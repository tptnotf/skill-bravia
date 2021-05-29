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
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler


class BraviaSkill(MycroftSkill):

    def initialize(self):
        super.base_url = 'http://' + self.settings.get("tv_ip") + "/sony/"
        super.key = self.settings.get("tv_password")

    @intent_handler(IntentBuilder('ChannelIntent').require('Channel').optionally('Number'))
    def handle_change_channel_intent(self, message):
        channel_number = message.data.get("Number")
        self.speak_dialog("change.channel", {'number': channel_number})

    @intent_handler(IntentBuilder('VolumeUpIntent').require('TV').require('Volume').require('Up'))
    def handle_change_channel_intent(self, message):
        self.speak_dialog("volume.up")
        volume_raise()

    @intent_handler(IntentBuilder('VolumeDownIntent').require('TV').require('Volume').require('Down'))
    def handle_change_channel_intent(self, message):
        self.speak_dialog("volume.down")
        volume_lower()


def create_skill():
    return BraviaSkill()


base_url = 'http://192.168.1.208/sony/'
key = 'a4G2H3f3sd5G8JU2'

headers = {
    'X-Auth-PSK': key
}

# COMMON METHODS


def post_request(url, data):
    return requests.post(url, data=json.dumps(data).encode("UTF-8"), headers=headers)


# GUIDE SERVICE


guide_url = base_url + 'guide'


def get_supported_api_info():
    data = {
        "method": "getSupportedApiInfo",
        "id": 101,
        "params": [{
            "services": ["system", "avContent"]
        }],
        "version": "1.0"
    }
    return post_request(guide_url, data)


# APP CONTROL SERVICE


app_control_url = base_url + 'appControl'


def get_application_list():
    data = {
        "method": "getApplicationList",
        "id": 201,
        "params": [],
        "version": "1.0"
    }

    return post_request(app_control_url, data)


def get_application_status_list():
    data = {
        "method": "getApplicationStatusList",
        "id": 202,
        "params": [],
        "version": "1.0"
    }

    return post_request(app_control_url, data)


def get_text_form():
    data = {
        "method": "getTextForm",
        "id": 203,
        "params": [{}],
        "version": "1.1"
    }

    return post_request(app_control_url, data)


def get_web_app_status():
    data = {
        "method": "getWebAppStatus",
        "id": 204,
        "params": [],
        "version": "1.0"
    }

    return post_request(app_control_url, data)


def set_active_app(uri):
    data = {
        "method": "setActiveApp",
        "id": 205,
        "params": [{
            "uri": uri
        }],
        "version": "1.0"
    }

    return post_request(app_control_url, data)


def set_text_form(text):
    data = {
        "method": "setTextForm",
        "id": 206,
        "params": [{
            "encKey": "",
            "text": text
        }],
        "version": "1.1"
    }

    return post_request(app_control_url, data)


def terminate_apps():
    data = {
        "method": "terminateApps",
        "id": 207,
        "params": [],
        "version": "1.0"
    }

    return post_request(app_control_url, data)


# AUDIO SERVICE


audio_url = base_url + 'audio'


def get_sound_settings():
    data = {
        "method": "getSoundSettings",
        "id": 301,
        "params": [{"target": ""}],
        "version": "1.1"
    }

    return post_request(audio_url, data)


def get_speaker_settings():
    data = {
        "method": "getSpeakerSettings",
        "id": 302,
        "params": [{"target": ""}],
        "version": "1.0"
    }

    return post_request(audio_url, data)


def get_volume_information():
    data = {
        "method": "getVolumeInformation",
        "id": 303,
        "params": [],
        "version": "1.0"
    }

    return post_request(audio_url, data)


def set_audio_mute(status):
    data = {
        "method": "setAudioMute",
        "id": 304,
        "params": [{
            "status": status
        }],
        "version": "1.0",
    }

    return post_request(audio_url, data)


def mute():
    return set_audio_mute(True)


def unmute():
    return set_audio_mute(False)


def set_audio_volume(volume):
    data = {
        "method": "setAudioVolume",
        "id": 305,
        "params": [{
            "volume": volume,
            "ui": "on",
            "target": "speaker"
        }],
        "version": "1.2"
    }

    return post_request(audio_url, data)


def volume_raise():
    set_audio_volume('+2')


def volume_lower():
    set_audio_volume('-2')


def set_sound_settings(settings):
    data = {
        "method": "setSoundSettings",
        "id": 306,
        "params": [{"settings": settings}],
        "version": "1.1"
    }

    return post_request(audio_url, data)


def set_speaker_settings(settings):
    data = {
        "method": "setSpeakerSettings",
        "id": 307,
        "params": [{"settings": settings}],
        "version": "1.0"
    }

    return post_request(audio_url, data)


# AV CONTENT SERVICE


av_content_url = base_url + 'avContent'


def get_content_count(source, type, target):
    data = {
        "method": "getContentCount",
        "id": 401,
        "params": [{
            "source": source,
            "type": type,
            "target": target
        }],
        "version": "1.0"
    }

    return post_request(av_content_url, data)


def get_content_list(uri, st_idx, cnt):
    data = {
        "method": "getContentList",
        "id": 402,
        "params": [{
            "uri": uri,
            "stIdx": st_idx,
            "cnt": cnt
        }],
        "version": "1.5"
    }

    return post_request(av_content_url, data)


def get_current_external_inputs_status():
    data = {
        "method": "getCurrentExternalInputsStatus",
        "id": 403,
        "params": [],
        "version": "1.1"
    }

    return post_request(av_content_url, data)


def get_scheme_list():
    data = {
        "method": "getSchemeList",
        "id": 404,
        "params": [],
        "version": "1.0"
    }

    return post_request(av_content_url, data)


def get_source_list(scheme):
    data = {
        "method": "getSourceList",
        "id": 405,
        "params": [{"scheme": scheme}],
        "version": "1.0"
    }

    return post_request(av_content_url, data)


def get_playing_content_info():
    data = {
        "method": "getPlayingContentInfo",
        "id": 406,
        "params": [],
        "version": "1.0"
    }

    return post_request(av_content_url, data)


def set_play_content(uri):
    data = {
        "method": "setPlayContent",
        "id": 407,
        "params": [{"uri": uri}],
        "version": "1.0"
    }

    return post_request(av_content_url, data)


# ENCRYPTION SERVICE


encryption_url = base_url + 'encryption'


def get_public_key():
    data = {
        "method": "getPublicKey",
        "id": 501,
        "params": [],
        "version": "1.0"
    }

    return post_request(encryption_url, data)


# SYSTEM SERVICE


system_url = base_url + 'system'


def get_current_time():
    data = {
        "method": "getCurrentTime",
        "id": 601,
        "params": [],
        "version": "1.1"
    }

    return post_request(system_url, data)


def get_interface_information():
    data = {
        "method": "getInterfaceInformation",
        "id": 602,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_led_indicator_status():
    data = {
        "method": "getLEDIndicatorStatus",
        "id": 603,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_network_settings():
    data = {
        "method": "getNetworkSettings",
        "id": 604,
        "params": [{"netif": ""}],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_power_saving_mode():
    data = {
        "method": "getPowerSavingMode",
        "id": 605,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_power_status():
    data = {
        "method": "getPowerStatus",
        "id": 606,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_remote_controller_info():
    data = {
        "method": "getRemoteControllerInfo",
        "id": 607,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_remote_device_settings():
    data = {
        "method": "getRemoteDeviceSettings",
        "id": 608,
        "params": [{"target": ""}],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_system_information():
    data = {
        "method": "getSystemInformation",
        "id": 609,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_system_supported_function():
    data = {
        "method": "getSystemSupportedFunction",
        "id": 610,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def get_wol_mode():
    data = {
        "method": "getWolMode",
        "id": 611,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def request_reboot():
    data = {
        "method": "requestReboot",
        "id": 612,
        "params": [],
        "version": "1.0"
    }

    return post_request(system_url, data)


def set_led_indicator_status(mode, status):
    data = {
        "method": "setLEDIndicatorStatus",
        "id": 613,
        "params": [{
            "mode": mode,
            "status": status
        }],
        "version": "1.1"
    }

    return post_request(system_url, data)


def set_language(language):
    data = {
        "method": "setLanguage",
        "id": 614,
        "params": [{"language": language}],
        "version": "1.0"
    }

    return post_request(system_url, data)


def set_power_saving_mode(mode):
    data = {
        "method": "setPowerSavingMode",
        "id": 615,
        "params": [{"mode": mode}],
        "version": "1.0"
    }

    return post_request(system_url, data)


def set_power_status(status):
    data = {
        "method": "setPowerStatus",
        "id": 616,
        "params": [{"status": status}],
        "version": "1.0"
    }

    return post_request(system_url, data)


def power_on():
    return set_power_status(True)


def power_off():
    return set_power_status(False)


def set_wol_mode(mode):
    data = {
        "method": "setWolMode",
        "id": 617,
        "params": [{"enabled": mode}],
        "version": "1.0"
    }

    return post_request(system_url, data)


# VIDEO SCREEN SERVICE


video_screen_url = base_url + 'videoScreen'


def set_scene_setting(scene):
    data = {
        "method": "setSceneSetting",
        "id": 701,
        "params": [{"value": scene}],
        "version": "1.0"
    }

    return post_request(video_screen_url, data)
