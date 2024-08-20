import os

from skabenclient.config import SystemConfig
from skabenclient.main import start_app

from config import CursesConfig
from device import CursesDevice

root = os.path.abspath(os.path.dirname(__file__))

sys_config_path = os.path.join(root, "conf", "system.yml")
dev_config_path = os.path.join(root, "conf", "device.yml")


if __name__ == "__main__":
    #
    # DO NOT FORGET TO RUN ./pre-run.sh install BEFORE FIRST START
    #

    app_config = SystemConfig(sys_config_path, root=root)
    dev_config = CursesConfig(dev_config_path)
    device = CursesDevice(app_config, dev_config)
    start_app(app_config=app_config, device=device)
