from dotty_dict import dotty


def dotty_list(lst: list) -> list:
    new_list = []
    for item in lst:
        if isinstance(item, dict):
            new_list.append(dotty_dict(item))
        elif isinstance(item, list):
            new_list.append(dotty_list(item))
        else:
            new_list.append(item)
    return new_list


def dotty_dict(obj: dict) -> dict:
    new_obj = {}
    for key, value in obj.items():
        data = dotty()
        if isinstance(value, dict):
            data[key] = dotty_dict(value)
        elif isinstance(value, list):
            data[key] = dotty_list(value)
        else:
            data[key] = value
        new_obj = new_obj | data.to_dict()
    return new_obj
