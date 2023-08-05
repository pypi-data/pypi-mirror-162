import numpy as np
from smartcapture.utils import getFromDict


class SCQLPredicate:
    def __init__(self, predicate, autotags):
        self.predicate = predicate
        self.autotags = autotags

    def evaluate(self, state):
        if type(self.predicate) != dict:
            return self.predicate
        if len(self.predicate) == 1:
            key = list(self.predicate)[0]
            if key == "$and":
                return ANDExpression(self.predicate["$and"], self.autotags).evaluate(state)
            elif key == "$or":
                return ORExpression(self.predicate["$or"], self.autotags).evaluate(state)
            elif key == "$not":
                return not SCQLPredicate(self.predicate["$not"], self.autotags).evaluate(state)
            else:
                return ConditionOnField(key, self.predicate[key], self.autotags).evaluate(state)
        else:  # default to AND predicate mimicking MongoQL behavior
            and_predicate = [{k: v} for k, v in self.predicate.items()]
            return ANDExpression(and_predicate, self.autotags).evaluate(state)


class ANDExpression(SCQLPredicate):
    def evaluate(self, state):
        for condition in self.predicate:
            value = SCQLPredicate(condition, self.autotags).evaluate(state)
            if value is False:
                return False
        return True


class ORExpression(SCQLPredicate):
    def evaluate(self, state):
        for condition in self.predicate:
            value = SCQLPredicate(condition, self.autotags).evaluate(state)
            if value is True:
                return True
        return False


class ConditionOnField:
    def __init__(self, field, predicate, autotags):
        self.field = field.split(".")
        self.predicate = predicate
        self.autotags = autotags

    def evaluate(self, state):
        field_value = getFromDict(state, self.field)
        key = list(self.predicate)[0]
        if key == "$eq":
            return field_value == self.predicate[key]
        elif key == "$neq":
            return field_value != self.predicate[key]
        elif key == "$gt":
            return field_value > self.predicate[key]
        elif key == "$gte":
            return field_value >= self.predicate[key]
        elif key == "$lt":
            return field_value < self.predicate[key]
        elif key == "$lte":
            return field_value <= self.predicate[key]
        elif key == "$in":
            return field_value in self.predicate[key]
        elif key == "$autotag":
            autotag_id, threshold = self.predicate[key][0], self.predicate[key][1]
            autotag_coefficients = self.autotags[autotag_id]
            autotag_value = np.dot(field_value.detach().numpy()[0], autotag_coefficients)
            print(autotag_value)
            return autotag_value >= threshold
        else:
            raise Exception  # TODO
