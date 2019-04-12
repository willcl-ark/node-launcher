import codecs
import os
from typing import List

# noinspection PyPackageRequirements
# noinspection PyProtectedMember,PyPackageRequirements
from google.protobuf.json_format import MessageToDict
from lnd_grpc.lnd_grpc import Client, ln, lnrpc

from node_launcher.logging import log

os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'


class DefaultModel(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class PendingChannels(DefaultModel):
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None


class LndClient(Client):
    def __init__(self,
                 lnd=None,
                 lnddir: str = None,
                 grpc_port: int = '10009',
                 grpc_host: str = 'localhost',
                 macaroon_path: str = None):
        super().__init__(lnd_dir=lnddir,
                         macaroon_path=macaroon_path,
                         network=lnd.bitcoin.network,
                         grpc_host=grpc_host,
                         grpc_port=str(grpc_port))
        self.lnd = lnd

    def get_info(self) -> ln.GetInfoResponse:
        request = ln.GetInfoRequest()
        response = self.lightning_stub.GetInfo(request, timeout=1)
        return response

    def get_node_info(self, pub_key: str) -> ln.NodeInfo:
        request = ln.NodeInfoRequest()
        request.pub_key = pub_key
        response = self.lightning_stub.GetNodeInfo(request, timeout=30)
        return response

    def connect_peer(self, pubkey: str, host: str,
                     timeout: int = 3) -> ln.ConnectPeerResponse:
        address = ln.LightningAddress(pubkey=pubkey, host=host)
        request = ln.ConnectPeerRequest(addr=address)
        response = self.lightning_stub.ConnectPeer(request, timeout=timeout)
        return response

    def list_channels(self) -> List[ln.Channel]:
        request = ln.ListChannelsRequest()
        request.active_only = False
        request.inactive_only = False
        request.public_only = False
        request.private_only = False
        response = self.lightning_stub.ListChannels(request, timeout=30)
        return response.channels

    def list_pending_channels(self) -> List[PendingChannels]:
        request = ln.PendingChannelsRequest()
        response = self.lightning_stub.PendingChannels(request, timeout=5)
        pending_channels = []
        pending_types = [
            'pending_open_channels',
            'pending_closing_channels',
            'pending_force_closing_channels',
            'waiting_close_channels'
        ]
        for pending_type in pending_types:
            for pending_channel in getattr(response, pending_type):
                channel_dict = MessageToDict(pending_channel)
                nested_data = channel_dict.pop('channel')
                # noinspection PyDictCreation
                flat_dict = {**channel_dict, **nested_data}
                flat_dict['pending_type'] = pending_type
                pending_channel_model = PendingChannels(**flat_dict)
                pending_channels.append(pending_channel_model)
        return pending_channels

    def open_channel(self, **kwargs):
        kwargs['node_pubkey'] = codecs.decode(kwargs['node_pubkey_string'],
                                              'hex')
        request = ln.OpenChannelRequest(**kwargs)
        log.debug('open_channel', request=MessageToDict(request))
        response = self.lightning_stub.OpenChannel(request)
        return response

    def get_graph(self) -> ln.ChannelGraph:
        request = ln.ChannelGraphRequest()
        request.include_unannounced = True
        log.debug('get_graph', request=MessageToDict(request))
        response = self.lightning_stub.DescribeGraph(request)
        return response
