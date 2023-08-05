def skip_footer(data, i):
    if i > 0:
        data = {k: v[:-i] for k, v in data.items()}
    return data


def make_key(idx, key):
    if key is None or key == '':
        return str(idx)
    return key
