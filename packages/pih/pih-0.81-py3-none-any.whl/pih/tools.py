
import json
import os
import sys
from typing import Any, Dict, List


from pih.collection import FieldItem, FieldItemList
from pih.const import DATA_EXTRACTOR, FIELD_NAME_COLLECTION


class DataTools:

    @staticmethod
    def represent(data: FieldItemList) -> str:
        return json.dumps(data, cls=FieldItemListEncoder)

    @staticmethod
    def rpc_represent(data: Dict) -> str:
        return json.dumps(data) if data is not None else ""

    @staticmethod
    def rpc_unrepresent(value: str) -> dict:
        return json.loads(value) if value is not None and value != "" else {}
        
    @staticmethod
    def unrepresent(value: str) -> dict:
        object: dict = json.loads(value)
        fields = object["fields"]
        data = object["data"]
        field_list: List = []
        for field_item in fields:
            for field_name in field_item:
                field_item_data = field_item[field_name]
                field_list.append(FieldItem(field_item_data["name"], field_item_data["caption"], bool(
                    field_item_data["visible"])))
        return DataPack.pack(FieldItemList(field_list), data)

class DataPack:
    
    @staticmethod
    def pack(fields: FieldItemList, data: Any) -> Dict:
        return {"fields": fields, "data": data}

    @staticmethod
    def pack_with_fields_name(fields_name: FieldItemList, data: Any) -> Dict:
        return {"fields": fields_name, "data": data}


class DataUnpack:

    @staticmethod
    def unpack(data: Dict, name: str = DATA_EXTRACTOR.AS_IS) -> Any:
        data_fields = data["fields"]
        return data_fields, DataUnpack.unpack_data(data, name)

    @staticmethod
    def unpack_data(data: Dict, name: str = DATA_EXTRACTOR.AS_IS):
        data_result = None
        data_data = data["data"]
        if name == DATA_EXTRACTOR.AS_IS:
            data_result = data_data
        elif name == DATA_EXTRACTOR.USER_NAME:
            data_result = str(
                data_data[FIELD_NAME_COLLECTION.NAME_FULL]).split(" ")[0],
        elif name == DATA_EXTRACTOR.USER_NAME_FULL:
            data_result = data_data[FIELD_NAME_COLLECTION.NAME_FULL]
        return data_result


class PathTools:

    @staticmethod
    def get_current_full_path(file_name: str) -> str:
        return os.path.join(sys.path[0], file_name)


class FieldItemListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FieldItem):
            return {f"{obj.name}": obj.__dict__}
        if isinstance(obj, FieldItemList):
            return obj.list
        return json.JSONEncoder.default(self, obj)
