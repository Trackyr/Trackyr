# tools to manipulate dicts and lists

# get the last n items in a dictionary assuming its ordered
def get_last_items(n, dict):
    result = {}
    for a in list(dict)[-3:]:
        result[a] = dict[a]

    return result
