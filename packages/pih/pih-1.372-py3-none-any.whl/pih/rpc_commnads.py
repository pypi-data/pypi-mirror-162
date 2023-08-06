from dataclasses import dataclass
from pih.collection import FullName

from pih.const import CONST
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
            return rpcCommand(CONST.HOST.ORION.NAME(), CONST.RPC.PORT(), command_name)

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

        @staticmethod
        def get_all_persons() -> bool:
            return RPC.call(RPC_COMMANDS.ORION.create_rpc_command("get_all_persons"))

            
    class AD:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(CONST.HOST.AD.NAME(), CONST.RPC.PORT(), command_name)

        @staticmethod
        def user_is_exsits_by_login(value: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("user_is_exsits_by_login"), value))

    
        @staticmethod
        def user_set_telephone(user_dn: str, telephone: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("user_set_telephone"), (user_dn, telephone)))


        @staticmethod
        def get_user_by_full_name(value: FullName) -> dict:
            return RPC.call(RPC_COMMANDS.AD.create_rpc_command("get_user_by_full_name"), value)

        @staticmethod
        def get_user_by_name(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.AD.create_rpc_command("get_user_by_name"), value)

        @staticmethod
        def get_user_by_login(value: str)-> dict:
            return RPC.call(RPC_COMMANDS.AD.create_rpc_command("get_user_by_login"), value)

        @staticmethod
        def get_templated_users() -> dict:
            return RPC.call(RPC_COMMANDS.AD.create_rpc_command("get_templated_users"))

        def get_containers() -> dict:
            return RPC.call(RPC_COMMANDS.AD.create_rpc_command("get_containers"))

        @staticmethod
        def create_user_from_template(templated_user_dn: str, full_name: FullName, login: str, password: str, description: str, telephone: str, email: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("create_user_from_template"), (templated_user_dn, full_name, login, password, description, telephone, email)))

        @staticmethod
        def create_user_in_container(container_dn: str, full_name: FullName, login: str, password: str, description: str, telephone: str, email: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.AD.create_rpc_command("create_user_in_container"), (container_dn, full_name, login, password, description, telephone, email)))


