import base64
import requests
from .trigger import Trigger
import json
from .constants import SMARTCAPTURE_ENDPOINT


class SmartCaptureClient:
    def __init__(self, api_key, device_name, preview=False):
        self.api_key = api_key
        self.encoded_key = base64.b64encode((self.api_key + ":").encode()).decode()
        self.device_name = device_name
        self.triggers = []
        if not preview:
            self.device_id = self._get_device_id()

    def _get_device_id(self):
        resp = requests.get(
            f"{SMARTCAPTURE_ENDPOINT}/all_devices",
            headers={"Authorization": "Basic " + self.encoded_key},
        )
        for device in resp.json():
            if device["name"] == self.device_name:
                return device["id"]
        raise Exception("Device not registered on smart capture")

    def _deserialize_triggers(self, trigger_config):
        last_activations = {
            trigger.trigger_id: trigger.last_activation for trigger in self.triggers
        }

        trigger_objects = []
        for trigger in trigger_config:
            trigger_objects.append(
                Trigger(
                    trigger,
                    json.dumps(trigger_config[trigger]["predicate"]),
                    trigger_config[trigger]["metadata"],
                )
            )
            if trigger in last_activations:
                trigger_objects[-1].last_activation = last_activations[trigger]

        return trigger_objects

    def load(self, trigger_config):
        """
        Loads triggers from json object or json file on device and prepares them for evaluation.

        Args:
        trigger_config: String containing path the json file with serialized trigggers or
            json object with serialized triggers.
        """
        if type(trigger_config) == str:
            data = json.load(open(trigger_config))
            self.triggers = self._deserialize_triggers(data)
        elif type(trigger_config) == dict:
            self.triggers = self._deserialize_triggers(trigger_config)

    def evaluate(self, state):
        return [
            (trigger.trigger_id, trigger.evaluate(state), trigger.dataset_id)
            for trigger in self.triggers
        ]
