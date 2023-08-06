import argparse
import os

from .generate import generate
from .deploy import deploy
from .constants import (
    GENPIP_DIR,
    TEMPLATES_DIR,
    SETUP_TEMPLATE_FILE_PATH,
    SETUP_TEMPLATE_URL,
)
from .ascii import BLUE_START, BOLD_START, DESIGN_END


def init():
    os.makedirs(GENPIP_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

    os.system(
        f"wget -O {SETUP_TEMPLATE_FILE_PATH} {SETUP_TEMPLATE_URL} > /dev/null 2>&1"
    )
    print(f"{BOLD_START}Downloaded setup.py template{DESIGN_END}")


def run():
    parser = argparse.ArgumentParser(
        description="GenPip: Create and deploy python packages to pypi.org"
    )
    parser.add_argument(
        "-g", "--generate", action="store_true", help="Generate a new package"
    )
    parser.add_argument(
        "-d", "--deploy", action="store_true", help="Deploy a package to pypi.org"
    )
    parser.add_argument(
        "-m", "--mock", action="store_true", help="Mock a deployment (no actual upload)"
    )

    args = parser.parse_args()

    if not os.path.exists(GENPIP_DIR) or not os.path.exists(TEMPLATES_DIR):
        print(f"{BLUE_START}Downloading templates...{DESIGN_END}")
        init()

    if args.generate:
        generate()
    elif args.deploy:
        deploy()
    elif args.mock:
        deploy(mock=True)
