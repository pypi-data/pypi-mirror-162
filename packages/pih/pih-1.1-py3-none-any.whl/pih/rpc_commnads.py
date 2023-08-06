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
        def rename_person_by_tab_number(new_full_name: FullName, tab_number: str) -> bool:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("rename_person_by_tab_number"), (new_full_name, tab_number))
        
        @staticmethod
        def make_mark_as_free_by_tab_number(tab_number: str) -> bool:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("make_mark_as_free_by_tab_number"), tab_number)


    class AD:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.AD.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def user_is_exsits_by_login(value: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("user_is_exsits_by_login"), value))

        @staticmethod
        def get_user_by_full_name(value: FullName) -> dict:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("get_user_by_full_name"), value))
