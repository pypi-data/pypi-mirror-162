import os


HOME_DIR = os.path.expanduser("~")
GENPIP_DIR = os.path.join(HOME_DIR, ".genpip")
TEMPLATES_DIR = os.path.join(GENPIP_DIR, "templates")
SETUP_TEMPLATE_FILE_PATH = os.path.join(TEMPLATES_DIR, "setup.py")

SETUP_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/frankhart2018/genpylib/master/data/setup.py"
)
