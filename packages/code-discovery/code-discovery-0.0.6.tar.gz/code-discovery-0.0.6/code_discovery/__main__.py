from typing import Optional

import click
import pkg_resources

from code_discovery.imports import get_all_imports_of_project


@click.group()
@click.version_option(pkg_resources.get_distribution('code_discovery').version)
def cli():
    pass


@click.option('--project_path', '-p',
              type=click.Path(exists=True),
              required=True, help="Path of the project")
@click.option('--output_path', '-o',
              type=click.Path(), help="Path for save results")
@click.command()
def imports(project_path: str, output_path: Optional[str]):
    """
    @param project_path: the project path
    @param output_path: the output path for saving
    @return: None
    """
    imports_data = get_all_imports_of_project(project_path)
    imports_data_output = ''
    for index, item in enumerate(imports_data):
        if item:
            imports_data_output += item

        if (index + 1) % 5 == 0:
            imports_data_output += '\n'

        else:
            imports_data_output += ' '

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as file_obj:
            file_obj.write(imports_data_output)
        print(f"Results saved in {output_path}")
    else:
        print(imports_data_output)


cli.add_command(imports)
if __name__ == '__main__':
    cli()
