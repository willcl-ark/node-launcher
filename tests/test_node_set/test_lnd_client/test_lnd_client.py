from unittest.mock import MagicMock

import pytest

from node_launcher.node_set.lnd_client import LndClient


@pytest.fixture
def mocked_lnd_client(lnd_client: LndClient) -> LndClient:
    # generate initial stubs because they are @properties in lnd_grpc
    _t1 = lnd_client.lightning_stub
    _t2 = lnd_client.wallet_unlocker_stub
    # mock the hidden stubs
    lnd_client._w_stub = MagicMock()
    lnd_client._lightning_stub = MagicMock()
    return lnd_client


class TestLndClient(object):
    def test_wallet_unlocker(self, lnd_client: LndClient):
        assert lnd_client.wallet_unlocker_stub

    def test_generate_seed(self, mocked_lnd_client: LndClient):
        mocked_lnd_client.gen_seed()
        assert mocked_lnd_client.wallet_unlocker_stub.called_once()

    def test_initialize_wallet(self, mocked_lnd_client: LndClient):
        mocked_lnd_client.init_wallet(
            wallet_password='test_password',
            seed=['test', 'mnemonic']
        )
        assert mocked_lnd_client.wallet_unlocker_stub.called_once()

    def test_unlock(self, mocked_lnd_client: LndClient):
        mocked_lnd_client.unlock_wallet('test_password')
        assert mocked_lnd_client.wallet_unlocker_stub.called_once()
