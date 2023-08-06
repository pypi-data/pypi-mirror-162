"""
Run this script once after first creating your project from this template repo to personalize
it for own project.
This script is interactive and will prompt you for various inputs.
"""

from pathlib import Path
from typing import Generator, List, Tuple

import click
from click_help_colors import HelpColorsCommand
from rich import print
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.traceback import install

install(show_locals=True, suppress=[click])

REPO_BASE = (Path(__file__).parent / "..").resolve()

#FILES_TO_REMOVE = {
#    REPO_BASE / ".github" / "workflows" / "setup.yml",
#    # REPO_BASE / "scripts" / "personalize.py",
#    # REPO_BASE / "setup-requirements.txt",
#}

EXTENSIONS_TO_IGNORE = {
    "png", "jpg", '.DS_Store', "pdf", "tar", "pt", "npy"
}
PATHS_TO_IGNORE = {

    REPO_BASE / "README.md",
    REPO_BASE / ".git",
    REPO_BASE / "docs" / "source" / "_static" / "favicon.ico",
    REPO_BASE / "assets",
    REPO_BASE / "old"
}

GITIGNORE_LIST = [
    line.strip()
    for line in (REPO_BASE / ".gitignore").open().readlines()
    if line.strip() and not line.startswith("#")
]

REPO_NAME_TO_REPLACE = "l2hmc-qcd"
BASE_URL_TO_REPLACE = "https://github.com/saforem2/l2hmc-qcd"


def main(
    github_org: str, github_repo: str, package_name: str, dry_run: bool = False
):
    repo_url = f"https://github.com/{github_org}/{github_repo}"
    package_actual_name = package_name.replace("_", "-")
    package_dir_name = package_name.replace("-", "_")

    # Confirm before continuing.
    print(f"Repository URL set to: [link={repo_url}]{repo_url}[/]")
    print(f"Package name set to: [cyan]{package_actual_name}[/]")
    #if not yes:
    #    yes = Confirm.ask("Is this correct?")
    #if not yes:
    #    raise click.ClickException("Aborted, please run script again")

    # Delete files that we don't need.
    for path in FILES_TO_REMOVE:
        # assert path.is_file(), path
        if not path.is_file():
            print(f'Unable to locate {path}, continuing...')
        else:
            if not dry_run:
                path.unlink()
            else:
                print(f"Removing {path}")

    # Personalize remaining files.
    replacements = [
        (BASE_URL_TO_REPLACE, repo_url),
        (REPO_NAME_TO_REPLACE, github_repo),
        ("l2hmc", package_actual_name),
        ("src/l2hmc", package_dir_name),
    ]
    if dry_run:
        for old, new in replacements:
            print(f"Replacing '{old}' with '{new}'")
    for path in iterfiles(REPO_BASE):
        personalize_file(path, dry_run, replacements)

    # Rename 'l2hmc' directory to `package_dir_name`.
    if not dry_run:
        (REPO_BASE / "l2hmc").replace(REPO_BASE / package_dir_name)
    else:
        print(f"Renaming 'l2hmc' directory to '{package_dir_name}'")

    # Start with a fresh README.
    # readme_contents = f"""# {package_actual_name}\n"""
    # if not dry_run:
    #    with open(REPO_BASE / "README.md", "w+t") as readme_file:
    #        readme_file.write(readme_contents)
    #else:
    #    print("Replacing README.md contents with:\n", Markdown(readme_contents))

    install_example = Syntax("pip install -e '.[dev]'", "bash")
    print(
        "[green]\N{check mark} Success![/] You can now install your package locally in development mode with:\n",
        install_example,
    )


def iterfiles(dir: Path) -> Generator[Path, None, None]:
    assert dir.is_dir()
    for path in dir.iterdir():
        if path in PATHS_TO_IGNORE:
            continue

        if any([s in path.as_posix() for s in EXTENSIONS_TO_IGNORE]):
            continue


        is_ignored_file = False
        for gitignore_entry in GITIGNORE_LIST:
            if path.relative_to(REPO_BASE).match(gitignore_entry):
                is_ignored_file = True
                break
        if is_ignored_file:
            continue

        if path.is_dir():
            yield from iterfiles(path)
        else:
            yield path


def personalize_file(path: Path, dry_run: bool, replacements: List[Tuple[str, str]]):
    with path.open("r+t") as file:
        filedata = file.read()

    should_update: bool = False
    for old, new in replacements:
        if filedata.count(old):
            should_update = True
            filedata = filedata.replace(old, new)

    if should_update:
        if not dry_run:
            with path.open("w+t") as file:
                file.write(filedata)
        else:
            print(f"Updating {path}")


if __name__ == "__main__":
    github_org = 'saforem2'
    github_repo = 'l2hmc-qcd'
    package_name = 'l2hmc'

    main(github_org=github_org, github_repo=github_repo, package_name=package_name)






