import pytest
import os
import logging
from skabenclient.config import DeviceConfigExtended, SystemConfig


@pytest.fixture
def mock_system_config():
    class MockSystemConfig:

        def __init__(self, root='/root', asset_root='asset_root'):
            self.root = root
            self.data = {
                'asset_root': asset_root
            }

        @staticmethod
        def logger():
            return logging.getLogger('test_curses')

        def get(self, val, default=None):
            return self.data.get(val, default)

        def set(self, key, val):
            self.data[key] = val
            return self.data

        def _update_paths(self, *args):
            pass

    system_config = MockSystemConfig()
    yield system_config


@pytest.fixture(autouse=True)
def mock_device_config(mock_system_config):
    device_config = DeviceConfigExtended(config_path='fake_device_config.yml', system_config=mock_system_config)

    yield device_config

    os.remove('fake_device_config.yml')
    os.remove('fake_device_config.yml.lock')
