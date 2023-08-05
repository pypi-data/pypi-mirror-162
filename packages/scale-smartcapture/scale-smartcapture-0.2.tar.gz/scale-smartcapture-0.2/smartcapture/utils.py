from functools import reduce
import operator


def getFromDict(data_dict, dict_path_list):
    return reduce(operator.getitem, dict_path_list, data_dict)
