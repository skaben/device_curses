import os
import sys
import json

from skabenclient.config import SystemConfig
from skabenclient.helpers import get_mac
from skabenclient.main import start_app

from device import BoilerplateDevice
from config import BoilerplateConfig

root = os.path.abspath(os.path.dirname(__file__))

sys_config_path = os.path.join(root, 'conf', 'system.yml')
dev_config_path = os.path.join(root, 'conf', 'device.yml')


if __name__ == "__main__":
    #
    # DO NOT FORGET TO RUN ./pre-run.sh install BEFORE FIRST START
    #

    # setting system config (immutable)
    app_config = SystemConfig(sys_config_path, root=root)
    # making device config (mutable, in-game)
    dev_config = BoilerplateConfig(dev_config_path)
    # <-- perform specific device config operations
    # which should be run once before main program
    # like making asset paths if you using DeviceConfigExtendede
    # dev_config.make_asset_paths()

    # instantiating device
    device = BoilerplateDevice(app_config, dev_config)
    # <-- perform specific device operations
    # which should be run once before main program
    # like device.gpio_setup() for lock device

    # start application
    start_app(app_config=app_config,
              device=device)
