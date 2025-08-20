import os
import sys
import json
import subprocess
from pathlib import Path

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
os.chdir(parent_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def read_interface_version(interface_file="./interface.json") -> str:
    interface_path = Path(interface_file)

    if not interface_path.exists():
        return "unknown"

    try:
        with open(interface_path, "r", encoding="utf-8") as f:
            interface_data = json.load(f)
            return interface_data.get("version", "unknown")
    except Exception:
        return "unknown"


def read_pip_config() -> dict:
    config_dir = Path("./config")
    config_dir.mkdir(exist_ok=True)

    config_path = config_dir / "pip_config.json"
    default_config = {
        "enable_pip_install": True,
        "last_version": "unknown",
        "mirror": "https://mirrors.ustc.edu.cn/pypi/simple",
    }

    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_config


def update_pip_config(version) -> bool:
    config_path = Path("./config/pip_config.json")
    try:
        config = read_pip_config()
        config["last_version"] = version

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception:
        return False


def install_requirements(req_file="requirements.txt", mirror=None) -> bool:
    req_path = Path(req_file)
    if not req_path.exists():
        return False

    try:
        print("正在安装或更新环境...")
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(req_path),
            "--no-warn-script-location",
        ]

        if mirror:
            cmd.extend(["-i", mirror])

        subprocess.check_call(cmd)
        print("（以上日志若无「error」等字样则正常）")
        return True
    except:
        print("环境加载失败，请检查网络与环境后重新尝试！")
        return False


def check_and_install_dependencies():
    pip_config = read_pip_config()
    current_version = read_interface_version()
    last_version = pip_config.get("last_version", "unknown")
    enable_pip_install = pip_config.get("enable_pip_install", True)
    mirror = pip_config.get("mirror", None)

    if enable_pip_install and (
        current_version != last_version or current_version == "unknown"
    ):
        if install_requirements(mirror=mirror):
            update_pip_config(current_version)
