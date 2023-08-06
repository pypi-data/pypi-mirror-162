import click
import os
import toml
import subprocess

from datetime import date

MODULE_DIR = os.path.dirname(__file__)
MIT_LICENSE_TEMPLATE_PATH = os.path.join(MODULE_DIR, "MIT-LICENSE-template")
PYPROJECT_TEMPLATE_PATH = os.path.join(MODULE_DIR, "pyproject-template.toml")


@click.command()
@click.argument("name")
def mkpypac(name):
    os.mkdir(name)
    os.chdir(name)
    os.mkdir("tests")
    os.mkdir("src")
    pac_path = os.path.join("src", name.replace("-", "_"))
    os.mkdir(pac_path)
    os.mknod(os.path.join(pac_path, "__init__.py"))

    if click.confirm("Do you want to add MIT license?", default=True):
        with open(MIT_LICENSE_TEMPLATE_PATH) as f:
            mit_license_template = f.read()
        full_name = click.prompt("Enter full name for license")
        full_name = " ".join([word.capitalize() for word in full_name.split()])
        with open("LICENSE", "w") as f:
            f.write(
                mit_license_template.format(
                    year=date.today().year, full_name=full_name
                )
            )

    description = click.prompt("Enter brief description of the project")
    authors = click.prompt(
        "Enter author name", show_default=full_name, default=full_name
    )

    with open("README.md", "w") as f:
        f.writelines([f"# {name}\n", description])

    with open(PYPROJECT_TEMPLATE_PATH) as f:
        pyproject_json = toml.load(f)

    pyproject_json["project"]["name"] = name
    pyproject_json["project"]["description"] = description
    pyproject_json["project"]["authors"] = []
    for name in authors.split(","):
        pyproject_json["project"]["authors"].append({"name": name})

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject_json, f)

    subprocess.run(["git", "init"])
    subprocess.run(["git", "branch", "-m", "main"])

    with open(".gitignore", "a") as f:
        f.writelines(["venv/\n", "dist/\n", "__pycache__/\n", "*.egg-info\n"])

    click.echo(
        click.style(f"\nCreated a new package in {os.getcwd()}", fg="green")
    )
