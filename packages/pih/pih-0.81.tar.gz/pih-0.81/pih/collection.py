from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


@dataclass
class FieldItem:
    name: str
    caption: str
    visible: bool = True
    position: int = -1


@dataclass
class FullName:
    last_name: str = None
    first_name: str = None
    middle_name: str = None

    def to_string(self) -> str:
        return "".join([self.last_name, self.first_name, self.middle_name])


@dataclass
class LoginPasswordPair:
    login: str = None
    password: str = None


class FieldItemList:

    list: List[FieldItem]

    def __init__(self, *arg):
        self.list = []
        arg_list = list(arg)
        for arg_item in arg_list:
            if isinstance(arg_item, FieldItem):
                if arg_item.position == -1:
                    self.list.append(arg_item)
                else:
                    self.list.insert(arg_item.position, arg_item)
            elif isinstance(arg_item, FieldItemList):
                self.list.extend(arg_item.list)
            elif isinstance(arg_item, List):
                for item in arg_item:
                    if isinstance(item, FieldItem):
                        self.list.append(item)

    def get_list(self) -> List[FieldItem]:
        return self.list

    def get_name_list(self):
        return list(map(lambda x: str(x.name), self.list))

    def get_caption_list(self):
        return list(map(lambda x: str(x.caption), filter(lambda y: y.visible, self.list)))

    def visible(self, index: int, value: bool):
        self.list[index].visible = value
        return self


@dataclass
class CommandItem:
    group: str
    file_name: str
    description: str
    section: str = ""
    cyclic: bool = True
    confirm_for_continue: bool = True
    enable: bool = True


@dataclass
class CommandLinkItem:
    command_name: str
    data_extractor_name: str


@dataclass
class CommandChainItem:
    input_name: str
    description: str
    list: List[CommandLinkItem]
    confirm_for_continue: bool = True
    enable: bool = True


@dataclass
class LogCommand():
    message: str
    log_channel: Enum
    log_level: Enum
    params: Tuple = None


@dataclass
class ParamItem:
    name: str
    caption: str
    description: str = None
