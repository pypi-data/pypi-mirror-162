import datetime
import decimal
import enum
import json


class MyJsonify(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, decimal.Decimal):
            # return str(o)
            return float(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        # elif isinstance(obj, datetime.datetime):
        #     return obj.strftime("%Y-%m-%d %H:%M:%S")
        # elif isinstance(obj, datetime.date):
        #     return obj.strftime("%Y-%m-%d")
        # elif isinstance(obj, numpy.int64):
        #   return int(obj)
        # elif isinstance(obj, numpy.integer):
        #   return int(obj)
        # elif isinstance(obj, numpy.floating):
        #   return float(obj)
        # elif isinstance(obj, numpy.ndarray):
        #   return obj.tolist()
        elif isinstance(obj, enum.Enum):
            return obj.value
        # elif isinstance(obj, bson.objectid.ObjectId):
        #   return str(obj)

        # return super(MyJsonify, self).default(obj)
        return json.JSONEncoder.default(self, obj)


def json_from_string(content):
    return json.loads(content)


def json_stringify(content, indent=True):
    if indent:
        return json.dumps(content, indent=4)
    return json.dumps(content)


def json_file_content(json_filepath):
    try:
        with open(json_filepath) as fd:
            return json.load(fd)
    except Exception as err:
        print(f"[jsonutils] opening: {json_filepath}", err)
        return None


def json_file_print(json_filepath):
    json_body = json_file_content(json_filepath)
    print(json.dumps(json_body, indent=4))
    return json_body
