from PySide2.QtCore import QProcess

from node_launcher.services.loop_software import LoopSoftware


class Loop(object):
    software: LoopSoftware
    process: QProcess

    """
    By default loopd attempts to connect to the lnd instance running on localhost:10009 and reads
    the macaroon and tls certificate from ~/.lnd. This can be altered using command line flags.
    See loopd --help
    """

    def __init__(self):
        self.running = False
        self.software = LoopSoftware()
        self.process = QProcess()
        self.process.setProgram(self.software.lnd)
        self.process.setCurrentReadChannel(0)
        # self.process.setArguments(self.args)
        self.process.start()

    @property
    def node_port(self) -> str:
        # TODO: more logic here?
        port = '11010'
        return port

    @property
    def loop_cli(self) -> str:
        base_command = [
            f'"{self.software.lncli}"',
        ]
        # base_command += self.loop_cli_arguments()
        return ' '.join(base_command)
