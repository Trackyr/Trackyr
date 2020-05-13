# tools to manipulate dicts and lists

# get the last n items in a dictionary assuming its ordered
def get_last_items(n, dict):
    result = {}
    for a in list(dict)[-n:]:
        result[a] = dict[a]

    return result

# get the n most recent items in a dictionary assuming its ordered
def get_most_recent_items(n, dict):
    result = {}
    for a in list(dict)[:n]:
        result[a] = dict[a]

    return result