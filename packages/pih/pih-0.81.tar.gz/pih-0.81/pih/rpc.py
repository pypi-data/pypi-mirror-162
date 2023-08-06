from dataclasses import dataclass
from typing import Dict
import grpc

import pih.rpcCommandCall_pb2_grpc as pb2_grpc
import pih.rpcCommandCall_pb2 as pb2

from pih.const import HOST_COLLECTION, RPC_CONST
from pih.tools import DataTools


@dataclass
class rpcCommand:
    host: str
    port: int
    name: str


class RPC:

    class rpcCommandClient():

        def __init__(self, host: str, port: int):
            self.host = host
            self.server_port = port
            self.channel = grpc.insecure_channel(
                f"{self.host}:{self.server_port}")
            self.stub = pb2_grpc.UnaryStub(self.channel)

        def call_command(self, name: str, parameters: Dict = None):
            return self.stub.rpcCallCommand(pb2.rpcCommand(name=name, parameters=parameters))

    @staticmethod
    def call(command: rpcCommand, parameters: Dict = None) -> str:
        return RPC.rpcCommandClient(command.host, command.port).call_command(command.name,  DataTools.rpc_represent(parameters)).data

    class ORION:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.ORION.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def get_free_marks() -> str:
            return RPC.call(RPC.ORION.create_rpc_command("get_free_marks"))

        @staticmethod
        def get_free_marks_group_statistics() -> str:
            return RPC.call(RPC.ORION.create_rpc_command("get_free_marks_group_statistics"))

        @staticmethod
        def get_free_marks_by_group(group: Dict) -> str:
            return RPC.call(RPC.ORION.create_rpc_command("get_free_marks_by_group"), group)

    class AD:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.AD.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def generate_password(type: str) -> str:
            return RPC.call(RPC.ORION.create_rpc_command("generate_password"), type)
