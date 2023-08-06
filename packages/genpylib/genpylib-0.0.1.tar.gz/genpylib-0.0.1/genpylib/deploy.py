import os

from .ascii import RED_START, BLUE_START, DESIGN_END


def add_dependencies(setup_file_contents, setup_file_path):
    print(f"{BLUE_START}Collecting dependencies...{DESIGN_END}")
    os.system("pipreqs . --force > /dev/null 2>&1")
    with open("requirements.txt", "r") as f:
        requirements = f.read().split("\n")[:-1]
    os.system("rm requirements.txt")

    libraries = [library.split("==")[0].strip() for library in requirements]
    libraries.remove("setuptools")
    if len(libraries) == 0:
        print(f"{BLUE_START}No dependencies found!{DESIGN_END}")
        return

    install_requires_statement = f"\tinstall_requires={libraries},"

    setup_file_lines = setup_file_contents.split("\n")
    setup_file_lines = (
        setup_file_lines[:-1] + [install_requires_statement] + setup_file_lines[-1:]
    )
    setup_file_contents = "\n".join(setup_file_lines)

    with open(setup_file_path, "w") as f:
        f.write(setup_file_contents)
    print(f"{BLUE_START}setup.py file updated with dependencies!{DESIGN_END}")


def deploy(mock=False):
    setup_file_path = "setup.py"

    if not os.path.exists("setup.py"):
        print(
            f"{RED_START}Error: {DESIGN_END}No setup.py file found in current directory!"
        )
        exit(1)

    with open("setup.py", "r") as f:
        setup_file_contents = f.read()

    if not "install_requires" in setup_file_contents:
        add_dependencies(
            setup_file_contents=setup_file_contents, setup_file_path=setup_file_path
        )

    print(f"{BLUE_START}Building...{DESIGN_END}")
    os.system(f"python3 {setup_file_path} sdist bdist_wheel > /dev/null 2>&1")
    print(f"{BLUE_START}Checking...{DESIGN_END}")
    os.system(f"twine check dist/*")

    if not mock:
        print(f"{BLUE_START}Uploading...{DESIGN_END}")
        os.system(f"twine upload dist/*")
