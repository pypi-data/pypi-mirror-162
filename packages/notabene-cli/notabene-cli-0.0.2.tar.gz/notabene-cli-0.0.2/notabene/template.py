"""Template checking section of notabene cli."""

import logging
import shutil
from pathlib import Path
from typing import List

import click

from notabene.base import Project, base
from notabene.utils import is_snake_case

log = logging.getLogger(__name__)


def _echo_templates(templates: List[Path], title: str = "The available templates are:"):
    click.secho(title, fg="cyan", bold=True)
    for i, path in enumerate(templates):
        click.echo(f"[{i:>2}]\t{path.stem}")


def _select_template(templates: List[Path], template: str):
    if template == "":
        _echo_templates(templates)
        while True:
            template = click.prompt("Select one of your templates", default=0, type=int)
            if 0 <= template < len(templates):
                break
            click.echo(f"Error: Template index '{template}' does not exist.")
        template_path = templates[template]
    elif template.isdigit():
        if 0 <= int(template) < len(templates):
            template_path = templates[int(template)]
        else:
            raise click.BadOptionUsage(
                option_name="template",
                message=f"Template index '{template}' does not exist. "
                "Leave empty or call the list command to get a list of options.",
            )
    else:
        for path in templates:
            if path.stem == template:
                template_path = path
                break
        else:
            raise click.BadOptionUsage(
                option_name="template",
                message=f"Template name '{template}' does not exist. "
                "Leave empty or call the list command to get a list of options.",
            )
    log.info("Selected template located at %s", template_path)
    return template_path


@base.group()
@click.option(
    "--template-dir",
    "-t",
    type=click.Path(exists=True, file_okay=False),
)
@click.pass_obj
def template(project: Project, template_dir: click.Path):
    """Use, check and create templates."""
    if template_dir is not None:
        project.template_dir = Path(template_dir)


@template.command()
@click.option(
    "--name",
    "-n",
    type=str,
    default="",
    help="The name of the new template. An option prompt is shown if left empty.",
)
@click.argument("notebook", type=str)
@click.pass_obj
def create(project: Project, name: str, notebook: str):
    """Create a new template."""
    click.secho("Creating new template...", fg="cyan", bold=True)
    templates = project.get_templates()

    if name == "":
        while True:
            name = click.prompt("Pick a name for the template", type=str)
            if is_snake_case(name):
                if name not in [t.stem for t in templates]:
                    break
                click.echo(f"Error: The template '{name}' already exists.")
            else:
                click.echo(
                    "Error: The name of the template should be snake case. "
                    "For example: 'the_name_of_the_template'"
                )

    elif name in [t.stem for t in templates]:
        raise click.BadOptionUsage(
            option_name="name", message=f"A template with name '{name}' already exists."
        )
    template_path = (project.template_dir / name).with_suffix(".ipynb")

    if notebook == "":
        # Select one of the notabene templates
        # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
        # Implement this later
        pass  # pragma: no cover
    elif not Path(notebook).with_suffix(".ipynb").exists():
        abs_path = Path(notebook).with_suffix(".ipynb").resolve()
        raise click.BadArgumentUsage(f"The notebook '{abs_path}' does not exist.")
    else:
        notebook = Path(notebook).with_suffix(".ipynb")

    template_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(notebook, template_path)
    click.secho(
        f"Created template '{name}' using notebook '{notebook}'.", fg="cyan", bold=True
    )


@template.command(name="list")
@click.pass_obj
def list_command(project: Project):
    """List all of your templates."""
    templates = project.get_templates()
    if len(templates) > 0:
        _echo_templates(templates)
    else:
        click.secho("You don't have any templates yet.", fg="cyan", bold=True)
        click.echo("Create new templates using the 'create' command.")


@template.command()
@click.option(
    "--template",
    "-t",
    type=str,
    default="",
    help="The name or index of a template. An option prompt is shown by default.",
)
@click.argument("notebook", type=str)
@click.pass_obj
def use(project: Project, template: str, notebook: str):
    """Use one of your templates to create a new notebook.

    NOTEBOOK is the name of the new notebook. Adding `.ipynb` is optional.
    """
    notebook = Path(notebook).with_suffix(".ipynb")
    if notebook.exists():
        raise click.BadArgumentUsage(f"The file '{notebook}' already exists.")

    templates = project.get_templates()
    template_path = _select_template(templates=templates, template=template)

    notebook.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(template_path, notebook)

    click.secho(
        f"Created notebook '{notebook}' using template '{template_path.stem}'.",
        fg="cyan",
        bold=True,
    )
