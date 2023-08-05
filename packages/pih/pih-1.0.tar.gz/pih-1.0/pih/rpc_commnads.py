from dataclasses import dataclass
from pih.collection import FullName

from pih.const import HOST_COLLECTION, RPC_CONST
from pih.rpc import RPC
from pih.tools import DataTools


@dataclass
class rpcCommand:
    host: str
    port: int
    name: str


class RPC_COMMANDS:

    class ORION:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.ORION.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def get_free_marks() -> str:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("get_free_marks"))

        @staticmethod
        def get_mark_by_tab_number(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("get_mark_by_tab_number"), value)

        @staticmethod
        def get_mark_by_person_name(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("get_mark_by_person_name"), value)

        @staticmethod
        def get_free_marks_group_statistics() -> str:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("get_free_marks_group_statistics"))

        @staticmethod
        def get_free_marks_by_group(group: dict) -> str:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("get_free_marks_by_group"), group)

        @staticmethod
        def update_full_name_by_tab_number(full_name: FullName, tab_number: str) -> bool:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("update_full_name_by_tab_number"), DataTools.rpc_represent((full_name, tab_number)))

    class AD:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.AD.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def user_is_exsits_by_login(value: str) -> str:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("user_is_exsits_by_login"), value))
