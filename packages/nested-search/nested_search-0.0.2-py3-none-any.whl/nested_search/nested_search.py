import json
from deepdiff import DeepDiff

# Dictionary keys in Deep Diff results
DICTIONARY_ITEM_REMOVED_KEY = "dictionary_item_removed"
VALUES_CHANGED_KEY = "values_changed"
KEYS_AND_PARTIAL_VALUES = "partial"
KEYS_AND_VALUES = "all"
KEYS_ONLY = "keys"

validation_result = True


def item_generator(json_input, lookup_key):
    """
   Method to identify all values in nested json based on lookup key
   :param json_input: source json object to be searched
   :param lookup_key: key to be seardhed for
   :return: list of values for lookup key. None if no value is found for the look up key in json string
   """
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)


def deep_diff_executor(actual,expected, type_of_validation):
    """
   Method that invokes DeepDiff utility and analyses metadata to infer any differences
   :param expected: expected result json object
   :param actual: actual result json object
   :return: True if DeepDiff metadata shows all the key-value pairs of expected json is present in actual json
   """
    deepdiff_result = DeepDiff(expected, actual, ignore_order=True)
    items_removed = []
    values_changed = []
    if DICTIONARY_ITEM_REMOVED_KEY in deepdiff_result:
        items_removed = deepdiff_result[DICTIONARY_ITEM_REMOVED_KEY]
    if type_of_validation != KEYS_AND_PARTIAL_VALUES:
        if VALUES_CHANGED_KEY in deepdiff_result:
            values_changed = deepdiff_result[VALUES_CHANGED_KEY]
    if type_of_validation == KEYS_ONLY:
        return len(items_removed) <= 0
    else:
        return len(items_removed) <= 0 and len(values_changed) <= 0


def compare_json_partial_values(actual, expected):
    validation_result = True
    validation_keys = list(expected.keys())
    for i in range(0, len(validation_keys)):
        value_list = list(item_generator(actual, validation_keys[i]))
        if type(expected[validation_keys[i]]) is list:
            for key, value in expected[validation_keys[i]][0].items():
                if str(value) not in str(value_list[0][0][key]):
                    validation_result = validation_result and False
        elif str(expected[validation_keys[i]]) not in str(value_list):
            validation_result = False
    return validation_result


def deep_search_keys_and_values(actual, expected, type_of_validation):
    """
   Helper method to match list of keys and values in nested json
   :param expected: subset of json object that needs to be matched with complex nested json object
   :param needle_index: index of the json key found inside actual json object
   :return: True if key-value pair matches, False otherwise
   """
    validation_result = True
    validation_keys = list(expected.keys())
    json_root = actual[list(actual.keys())[0]]
    list_flag = type(json_root) is list
    # check if the source element is array so that we can extract nth element from array using index
    if list_flag:
        needle_index = find_needle_index_in_haystack(actual, expected)
        if needle_index == -1:
            validation_result = False
        else:
            validation_result = deep_diff_executor(expected, json_root[needle_index], type_of_validation)
            # Default deep diff would have verified only the keys , so its essential to validate values manually
            if type_of_validation == KEYS_AND_PARTIAL_VALUES:
                # check deep diff results before beginning value validation
                if validation_result:
                    validation_result = compare_json_partial_values(json_root[needle_index], expected)
    else:
        for i in range(1, len(validation_keys)):
            value_list = list(item_generator(actual, validation_keys[i]))
            if str(expected[validation_keys[i]]) not in str(value_list):
                validation_result = False
    return validation_result


def find_needle_index_in_haystack(haystack, needle):
    needle_index = -1
    validation_keys = list(needle.keys())
    value_list = list(item_generator(haystack, validation_keys[0]))
    for i in range(0, len(value_list)):
        if needle[validation_keys[0]] in value_list[i]:
            needle_index = i
    return needle_index


def deep_search_array(haystack, needle, type_of_validation):
    validation_result = True
    # Begin: This section is needed to extract only the required element from the actual response body
    haystack_keys = haystack.keys()
    if len(haystack_keys) > 1:
        validation_keys = list(needle.keys())
        value_list = list(item_generator(haystack, validation_keys[0]))
        # if there is matching list of key-value pair, construct that as the new source for validation
        if len(value_list) > 0:
            haystack = {validation_keys[0]: value_list[0]}
    # End: This section is needed to extract only the required element from the actual response body

    # iterated through each element of expected results
    if list(haystack.keys())[0] == list(needle.keys())[0]:
        needles = needle[list(needle.keys())[0]]
        for needle in needles:
            validation_result = validation_result and deep_search_keys_and_values(haystack, needle, type_of_validation)
    else:
        validation_result = False
    return validation_result


def json_deep_search (immutable_haystack, haystack, needle, type_of_validation):
    """
    Method to find very small subset of json object inside larger complex json object
    :param immutable_haystack :
    since this method will be called recursively, we store the actual result in another variable that doesn't get
    changed in recursive calls
    :param haystack: source json object
    :param needle: json object to be searched for
    :return: True, if all the key-value pair matches, False otherwise
    """

    global validation_result
    if type_of_validation == KEYS_ONLY:
        validation_result = deep_diff_executor(haystack,needle,type_of_validation)
    else:
        # check if the expected response to be compared is dict or list
        if type(needle) is dict:
            for key, value in needle.items():
                value_list = list(item_generator(immutable_haystack, key))
                if len(value_list) > 0:
                    if type(value) is int or type(value) is str:
                        if type_of_validation == KEYS_AND_PARTIAL_VALUES:
                            validation_result = validation_result and value in value_list
                        else:
                            validation_result = validation_result and value == value_list
                    elif type(value) is list:
                        haystack = {key: value_list[0]}
                        needle = {key: value}
                        validation_result = validation_result and deep_search_array(haystack, needle, type_of_validation)
                    elif type(value) is dict:
                        haystack = {key: value_list[0]}
                        needle = value
                        validation_result = validation_result and json_deep_search(immutable_haystack,haystack, needle, type_of_validation)
                else:
                    validation_result = False;
                    break
        # if expected response is a list
        else:
            validation_result = validation_result and deep_search_array(haystack, needle, type_of_validation)

    return validation_result


def DeepSearchJSON(actual_result,expected_result,type_of_validation):
    return json_deep_search(actual_result,actual_result,expected_result,type_of_validation)