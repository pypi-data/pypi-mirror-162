from smartcapture.scql import SCQLPredicate
import json
import time


class Trigger:
    def __init__(self, trigger_id, predicate, metadata):
        """
        Args:
        trigger_id: Unique identifier to identify triggers to be used
        predicate: Smart Capture Query predicate
        metadata: Additional data required to evaluate if a trigger should be activated.
        For example:
        {
            "autotags": {
                "tag_1": [0.5, 0.3, ...]
            },
            "sample_rate": 10,
        }

        """
        self.trigger_id = trigger_id
        self.autotags = metadata.get("autotags", {})
        self.sample_rate = metadata.get("sample_rate", 0)
        self.dataset_id = metadata.get("dataset_id", "")
        self.predicate = SCQLPredicate(json.loads(predicate), self.autotags)
        self.last_activation = 0

    def evaluate(self, state):
        """
        Evaluates if a trigger has been activated given the device state using the predicate

        Args:
        state: Dictionary containing state data of the device.

        Returns:
        boolean indicating if trigger was activated
        """
        if time.time()*1000.0 < self.last_activation + self.sample_rate:
            return False
        result = self.predicate.evaluate(state)  # TODO: wrap in a try except to catch key error
        if result:
            self.last_activation = time.time()*1000.0
        return result
