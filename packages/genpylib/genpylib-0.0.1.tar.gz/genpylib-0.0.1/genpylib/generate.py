import re
import os
from simplpy.list_.list_func import dump_list

from .ascii import GENPIP_ASCII_ART, RED_START, BOLD_START, DESIGN_END
from .compile import compile_template
from .constants import SETUP_TEMPLATE_FILE_PATH


def check_package_type(val):
    if val not in ["lib", "cli"]:
        raise ValueError(
            f"{RED_START}Error: {DESIGN_END}Type of package must be either 'lib' or 'cli'"
        )


def check_url(val):
    if not re.match(
        r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$",
        val,
    ):
        raise ValueError(f"{RED_START}Error: {DESIGN_END}URL must be valid")


def check_email(val):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", val):
        raise ValueError(f"{RED_START}Error: {DESIGN_END}Email must be valid")


def get_valid_input(propmpt, function):
    val = ""

    while True:
        try:
            val = input(f"{BOLD_START}{propmpt}: {DESIGN_END}")
            function(val=val)
            break
        except ValueError as e:
            print(e)

    return val


def create_project_dirs(name):
    os.makedirs(name, exist_ok=True)
    os.makedirs(os.path.join(name, name), exist_ok=True)


def create_init_file(name, version):
    init_path = os.path.join(name, name, "__init__.py")

    with open(init_path, "w") as f:
        f.write(f"__version__ = '{version}'")


def create_gitignore(name):
    gitignore_path = os.path.join(name, ".gitignore")

    ignore_list = [
        ".DS_Store",
        ".vscode/",
        ".idea/",
        "__pycache__/",
        "venv/",
        "dist/",
        "build/",
        "*.egg-info/",
    ]
    dump_list(ignore_list, gitignore_path)


def create_readme_file(name, description):
    readme_path = os.path.join(name, "README.md")

    with open(readme_path, "w") as f:
        f.write(f"# {name}\n\n{description}")


def generate():
    print(GENPIP_ASCII_ART)
    print("GenPip python package boilerplate generator")
    print("-------------------------------------------")

    name = input(f"{BOLD_START}Name: {DESIGN_END}")
    description = input(f"{BOLD_START}Description: {DESIGN_END}")
    url = get_valid_input(propmpt="GitHub URL/Documentation URL", function=check_url)
    author_name = input(f"{BOLD_START}Author Name: {DESIGN_END}")
    author_email = get_valid_input(propmpt="Author Email", function=check_email)
    license_ = input(f"{BOLD_START}License: {DESIGN_END}")
    python_support_oldest = int(
        input(f"{BOLD_START}Python Version Supported (Oldest): {DESIGN_END}")
    )
    python_support_latest = int(
        input(f"{BOLD_START}Python Version Supported (Newest): {DESIGN_END}")
    )
    license_classifier = input(f"{BOLD_START}License Classifier: {DESIGN_END}")
    type_of_package = get_valid_input(
        propmpt="Type of Package (lib/cli)", function=check_package_type
    )
    version = input(f"{BOLD_START}Version (Default = 0.0.1-alpha0): {DESIGN_END}")
    if not version:
        version = "0.0.1-alpha0"

    commands = []
    if type_of_package == "cli":
        number_of_commands = input(f"{BOLD_START}Number of Commands: {DESIGN_END}")

        for i in range(int(number_of_commands)):
            print(f"{BOLD_START}Command {i+1}) {DESIGN_END}")
            command = input(f"{BOLD_START}Command Name: {DESIGN_END}")
            file_name = input(f"{BOLD_START}Command File Name: {DESIGN_END}")
            function_name = input(f"{BOLD_START}Command Function Name: {DESIGN_END}")

            commands.append(f"{command} = {name}.{file_name}:{function_name}")

    config = {
        "name": name,
        "description": description,
        "url": url,
        "author_name": author_name,
        "author_email": author_email,
        "license": license_,
        "type_": type_of_package,
        "commands": commands,
        "license_classifier": license_classifier,
        "python_support_oldest": python_support_oldest,
        "python_support_latest": python_support_latest,
        "dependencies": [],
    }

    create_project_dirs(name=name)
    create_init_file(name=name, version=version)
    create_readme_file(name=name, description=description)
    create_gitignore(name=name)

    setup_path = os.path.join(name, "setup.py")
    compile_template(
        config=config, template_path=SETUP_TEMPLATE_FILE_PATH, dump_path=setup_path
    )
