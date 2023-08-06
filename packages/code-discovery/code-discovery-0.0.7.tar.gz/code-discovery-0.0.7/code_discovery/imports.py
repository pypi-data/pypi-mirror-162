import dis
import os
from typing import List, Set


def get_imports_of_file(path: str) -> Set[str]:
    """
    @param path: the file path
    @return: the module names that imported in file
    """

    with open(path, encoding='utf-8') as file_obj:
        code = file_obj.read()
    try:
        instructions = dis.get_instructions(code)
    except SyntaxError:
        return set()
    imports = [__ for __ in instructions if 'IMPORT_NAME' in __.opname]

    modules = set()
    for instr in imports:
        modules.add(instr.argval.split('.')[0])
    return modules


def is_project_python_file(directory_path: str, filename: str) -> bool:
    return os.path.splitext(filename)[1] == '.py' and \
           'site-packages' not in directory_path


def get_all_python_files(root_path: str) -> List[str]:
    """
    @param root_path: the root path
    @return: the python file paths under the root path
    """
    project_files = [os.path.join(directory_path, filename)
                     for directory_path, _, filenames in os.walk(root_path)
                     for filename in filenames if is_project_python_file(directory_path, filename)]
    return project_files


def get_all_imports_of_project(project_path: str) -> List[str]:
    """
    @param root_path: the project path
    @return: the module names that imported in all files of the project
    """
    project_files = get_all_python_files(project_path)
    imports = set()
    for file in project_files:
        file_imports = get_imports_of_file(file)
        imports.update(file_imports)
    return sorted(list(imports))
