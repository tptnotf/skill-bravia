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

from xml.etree.ElementTree import Element, SubElement, tostring


class Client:
    def __init__(self, name, ip, port=5555, access_key=None):
        self._name = name
        self._ip = ip
        self._port = port
        self._key = access_key or ''
        self._url = f"http://{self.ip}/sony/"
        if self.key:
            self._headers = {"X-Auth-PSK": self.key}
        else:
            self._headers = ''
        try:
            self._volume = self._get_volume_information()['result'][0][0]['volume']
            self.app_list = []
            self._populate_app_list()
            self.remote_codes = []
            self._populate_remote_codes()
            # Hack because for some reason the first code sent does not work.
            # I hope sending an empty string initilizes the command
            self.send_command("")
        except:
            pass

    @property
    def name(self):
        return self._name

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def key(self):
        return self._key

    @property
    def url(self):
        return self._url

    @property
    def headers(self):
        return self._headers

    @property
    def volume(self):
        return self._get_volume_information()['result'][0][0]['volume']

    @volume.setter
    def volume(self, value):
        info = self._get_volume_information()['result'][0][0]
        vol_min = info['minVolume']
        vol_max = info['maxVolume']
        if value >= vol_min and value <= vol_max:
            vol = str(value)
        elif value > vol_max:
            vol = str(vol_max)
        elif value < vol_min:
            vol = str(vol_min)
        self._volume = self._set_audio_volume(vol)


    @property
    def muted(self):
        return self._get_volume_information()['result'][0][0]['mute']

    @property
    def is_on(self):
        if self._get_power_status()['result'][0]['status'] == 'active':
            return True
        return False


    def get_request(self, service_url, data):
        url = f"{self.url}{service_url}"
        result = json.loads(requests.post(url, data=json.dumps(data).encode("UTF-8"), headers=self.headers).text)
        return result

    def post_request(self, service_url, data):
        url = f"{self.url}{service_url}"
        result = requests.post(url, data=json.dumps(data).encode("UTF-8"), headers=self.headers)
        return result

###############################
#
# Applications Section
#

    # Private becaus it is used to populate the app list
    # Get info from self.app_list
    def _get_application_list(self):
        data = {
            "method": "getApplicationList",
            "id": 201,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("appControl", data)

    # Sets the app on the client
    def set_active_app(self, uri):
        data = {
            "method": "setActiveApp",
            "id": 205,
            "params": [{
                "uri": uri
            }],
            "version": "1.0"
        }

        return self.post_request("appControl", data)

    # not used yet, maybe kills all apps?
    def terminate_apps(self):
        data = {
            "method": "terminateApps",
            "id": 207,
            "params": [],
            "version": "1.0"
        }

        return self.post_request("appControl", data)

#
# End App junk
#
#################################

#################################
#
# Text input junk
#

    def set_text_form(self, text):
        data = {
            "method": "setTextForm",
            "id": 206,
            "params": [{
                "encKey": "",
                "text": text
            }],
            "version": "1.1"
        }

        return self.post_request("appControl", data)

#
# End Text Input Junk
#
###############################

###############################
#
# Audio Stuff
#

    # Private because it is used for several properties
    def _get_volume_information(self):
        data = {
            "method": "getVolumeInformation",
            "id": 303,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("audio", data)

    ##############################
    #
    # Muting Stuff
    #

    # Private because it is used for properties
    def _set_audio_mute(self, status):
        data = {
            "method": "setAudioMute",
            "id": 304,
            "params": [{
                "status": status
            }],
            "version": "1.0",
        }

        return self.post_request("audio", data)


    def mute(self):
        return self._set_audio_mute(True)


    def unmute(self):
        return self._set_audio_mute(False)

    def toggle_mute(self):
        return self._set_audio_mute(not self.muted)

    #
    # End Muting Stuff
    #
    ############################

    ############################
    #
    # Volume Stuff
    #

    # private because used with functions and properties
    def _set_audio_volume(self, volume):
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

        return self.post_request("audio", data)

#
# End Sound Management
#
###############################

###############################
#
# Power Stuff
#

    # Private because its used for properties
    def _get_power_status(self):
        data = {
            "method": "getPowerStatus",
            "id": 606,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    def _set_power_status(self, status):
        data = {
            "method": "setPowerStatus",
            "id": 616,
            "params": [{"status": status}],
            "version": "1.0"
        }

        return self.post_request("system", data)

    def power_on(self):
        return self._set_power_status(True)


    def power_off(self):
        return self._set_power_status(False)

    def toggle_power(self):
        return self._set_power_status(not self.is_on)

    def request_reboot(self):
        data = {
            "method": "requestReboot",
            "id": 612,
            "params": [],
            "version": "1.0"
        }

        return self.post_request("system", data)

#
# End of Power Stuff
#
#############################

#############################
#
# Remote Control Junk
#

    # Gets the remote codes and used by _populate_remote_codes
    def _get_remote_controller_info(self):
        data = {
            "method": "getRemoteControllerInfo",
            "id": 607,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    def _populate_app_list(self):
        for app in self._get_application_list()['result'][0]:
            # self.app_list.append(ClientApp(app['title'], app['uri'], app['icon']))
            self.app_list.append(app)

    def _populate_remote_codes(self):
        for code in self._get_remote_controller_info()['result'][1]:
            self.remote_codes.append(code)

    #############################################
    # This section of code was coppied from
    # https://github.com/aparraga/braviarc/blob/f1c0cf81e4dfcb4eddd0643ab5759a79151d3877/braviarc/braviarc.py#L140-L180
    # Under a MIT License
    #
    def _send_req_ircc(self, params, log_errors=True):
        """Send an IRCC command via HTTP to Sony Bravia."""
        headers = {'SOAPACTION':
                   '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"'}

        if self.key is not None:
            headers['X-Auth-PSK'] = self.key

        root = Element('s:Envelope',
                       {"xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
                        "s:encodingStyle":
                            "http://schemas.xmlsoap.org/soap/encoding/"})
        body = SubElement(root, "s:Body")
        sendIRCC = SubElement(body, "u:X_SendIRCC",
                              {"xmlns:u":
                               "urn:schemas-sony-com:service:IRCC:1"})
        irccCode = SubElement(sendIRCC, "IRCCCode")
        irccCode.text = params

        xml_str = tostring(root, encoding='utf8')

        try:
            response = requests.post('http://' + self.ip + '/sony/IRCC',
                                     headers=headers,
                                     cookies=None,
                                     data=xml_str,
                                     timeout=10)
        except requests.exceptions.HTTPError as exception_instance:
            if log_errors:
                print("HTTPError: " + str(exception_instance))

        except requests.exceptions.Timeout as exception_instance:
            if log_errors:
                print("Timeout occurred: " + str(exception_instance))

        except Exception as exception_instance:  # pylint: disable=broad-except
            if log_errors:
                print("Exception: " + str(exception_instance))
        else:
            content = response.content
            return content

    def send_command(self, command):
        self._send_req_ircc(self.get_command_code(command))
    #
    # End of coppied code
    #
    ###################################
    def get_command_code(self, name):
        for code in self.remote_codes:
            if name == code["name"]:
                return code["value"]
        return None

#
# End of Remote Control Junk
#
###############################

###############################
#
# Unused functions
#

    # Not used, shows all possiable endpoints
    def get_supported_api_info(self):
        data = {
            "method": "getSupportedApiInfo",
            "id": 101,
            "params": [{
                "services": ["system", "avContent"]
            }],
            "version": "1.0"
        }
        return self.get_request("guide", data)

    # Not used, get public key stuff
    def get_public_key(self):
        data = {
            "method": "getPublicKey",
            "id": 501,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("encryption", data)

    # Not used. Not sure where I would
    def get_application_status_list(self):
        data = {
            "method": "getApplicationStatusList",
            "id": 202,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("appControl", data)

    # Not used. returns an error
    def get_text_form(self):
        data = {
            "method": "getTextForm",
            "id": 203,
            "params": [{}],
            "version": "1.1"
        }

        return self.post_request("appControl", data)

    # Not used. I believe this shows if a webbrowser is open
    def get_web_app_status(self):
        data = {
            "method": "getWebAppStatus",
            "id": 204,
            "params": [],
            "version": "1.0"
        }

        return self.post_request("appControl", data)

    # Not used. Gets the output device
    def get_sound_settings(self):
        data = {
            "method": "getSoundSettings",
            "id": 301,
            "params": [{"target": ""}],
            "version": "1.1"
        }

        return self.get_request("audio", data)

    # Not used. Gets settings of audio channels
    def get_speaker_settings(self):
        data = {
            "method": "getSpeakerSettings",
            "id": 302,
            "params": [{"target": ""}],
            "version": "1.0"
        }

        return self.get_request("audio", data)

    # Not used yet
    def set_sound_settings(self, settings):
        data = {
            "method": "setSoundSettings",
            "id": 306,
            "params": [{"settings": settings}],
            "version": "1.1"
        }

        return self.post_request("audio", data)

    # Not used yet
    def set_speaker_settings(self, settings):
        data = {
            "method": "setSpeakerSettings",
            "id": 307,
            "params": [{"settings": settings}],
            "version": "1.0"
        }

        return self.post_request("audio", data)

    # Not sure what these do

    # def get_content_count(self, source, type, target):
    #     data = {
    #         "method": "getContentCount",
    #         "id": 401,
    #         "params": [{
    #             "source": source,
    #             "type": type,
    #             "target": target
    #         }],
    #         "version": "1.0"
    #     }
    def get_content_count(self, source):
        data = {
            "method": "getContentCount",
            "id": 401,
            "params": [{
                "source": source
            }],
            "version": "1.0"
        }

        return self.post_request("avContent", data)

    # Not used yet
    def get_content_list(self, uri, stIdx=0, cnt=50):
        data = {
            "method": "getContentList",
            "id": 402,
            "params": [{
                "uri": uri,
                "stIdx": stIdx,
                "cnt": cnt
            }],
            "version": "1.5"
        }

        return self.get_request("avContent", data)

    # Not used yet
    def get_current_external_inputs_status(self):
        data = {
            "method": "getCurrentExternalInputsStatus",
            "id": 403,
            "params": [],
            "version": "1.1"
        }

        return self.get_request("avContent", data)

    # Not used yet
    def get_scheme_list(self):
        data = {
            "method": "getSchemeList",
            "id": 404,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("avContent", data)

    # Not used yet
    def get_source_list(self, scheme):
        data = {
            "method": "getSourceList",
            "id": 405,
            "params": [{"scheme": scheme}],
            "version": "1.0"
        }

        return self.get_request("avContent", data)

    # Not used yet
    def get_playing_content_info(self):
        data = {
            "method": "getPlayingContentInfo",
            "id": 406,
            "params": [],
            "version": "1.0"
        }

        return self.post_request("avContent", data)

    # Not used yet
    def set_play_content(self, uri):
        data = {
            "method": "setPlayContent",
            "id": 407,
            "params": [{"uri": uri}],
            "version": "1.0"
        }

        return self.post_request("avContent", data)

    # Dont need to use this
    def get_current_time(self):
        data = {
            "method": "getCurrentTime",
            "id": 601,
            "params": [],
            "version": "1.1"
        }

        return self.post_request("system", data)

    # Not used yet
    # Shows info about the tv
    def get_interface_information(self):
        data = {
            "method": "getInterfaceInformation",
            "id": 602,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used yet
    # Gets the brightness of the screen?
    # shows {"mode":"AutoBrightnessAdjust"}
    def get_led_indicator_status(self):
        data = {
            "method": "getLEDIndicatorStatus",
            "id": 603,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used yet
    # Does what it says DUHH
    def get_network_settings(self):
        data = {
            "method": "getNetworkSettings",
            "id": 604,
            "params": [{"netif": ""}],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used yet
    # Another DUHH thing
    def get_power_saving_mode(self):
        data = {
            "method": "getPowerSavingMode",
            "id": 605,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used yet
    # Not sure why I need this...at least yet
    def get_remote_device_settings(self):
        data = {
            "method": "getRemoteDeviceSettings",
            "id": 608,
            "params": [{"target": ""}],
            "version": "1.0"
        }

        return self.get_request("system", data)
    # Not used yet
    # Gets more system info
    def get_system_information(self):
        data = {
            "method": "getSystemInformation",
            "id": 609,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used yet
    # Shows WOL info
    def get_system_supported_function(self):
        data = {
            "method": "getSystemSupportedFunction",
            "id": 610,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used yet
    # Get the status of WOL
    def get_wol_mode(self):
        data = {
            "method": "getWolMode",
            "id": 611,
            "params": [],
            "version": "1.0"
        }

        return self.get_request("system", data)

    # Not used right now
    # Screen brightness?
    def set_led_indicator_status(self, mode, status):
        data = {
            "method": "setLEDIndicatorStatus",
            "id": 613,
            "params": [{
                "mode": mode,
                "status": status
            }],
            "version": "1.1"
        }

        return self.post_request("system", data)


    # Not used
    # Obviously sets the language
    def set_language(self, language):
        data = {
            "method": "setLanguage",
            "id": 614,
            "params": [{"language": language}],
            "version": "1.0"
        }

        return self.post_request("system", data)

    # Not used yet
    def set_power_saving_mode(self, mode):
        data = {
            "method": "setPowerSavingMode",
            "id": 615,
            "params": [{"mode": mode}],
            "version": "1.0"
        }

        return self.post_request("system", data)

    # Not used yet
    # Assume it turns WOL on and off
    def set_wol_mode(self, mode):
        data = {
            "method": "setWolMode",
            "id": 617,
            "params": [{"enabled": mode}],
            "version": "1.0"
        }

        return self.post_request("system", data)

    # Not used yet
    def set_scene_setting(self, scene):
        data = {
            "method": "setSceneSetting",
            "id": 701,
            "params": [{"value": scene}],
            "version": "1.0"
        }

        return self.post_request("videoScreen", data)
# response = get_public_key()
# print(response)
# print(response.text)

class ClientApp:
    def __init__(self, title, uri, icon=None):
        self.title = title
        self.uri = uri
        self.icon = icon # TODO: Create a default icon if none is provided

