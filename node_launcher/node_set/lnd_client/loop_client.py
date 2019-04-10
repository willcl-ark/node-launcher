from loop_rpc.loop_rpc import LoopClient


class LoopClient(LoopClient):
    def __init__(self,
                 loop_host: str = 'localhost',
                 loop_port: str = '11010'):
        super().__init__(loop_host=loop_host,
                         loop_port=loop_port)
