#!/usr/bin/env python
# coding: utf-8

import ast
import collections
import importlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Union

import requests
from autoflake import _main
from bs4 import BeautifulSoup
from rich.console import Console
from rich.syntax import Syntax
from yapf.yapflib.yapf_api import FormatCode


class _DummySpecLoader:
    loader = ''


class FormatPython:

    def __init__(self,
                 only_imports: bool = False,
                 in_place: bool = False,
                 show_line_numbers: bool = False,
                 style: str = 'pep8',
                 keep_external_unused_imports: bool = False,
                 keep_unused_imports: bool = False) -> None:
        self.only_imports = only_imports
        self.in_place = in_place
        self.show_line_numbers = show_line_numbers
        self.style = style
        self.keep_external_unused_imports = keep_external_unused_imports
        self.keep_unused_imports = keep_unused_imports

    @staticmethod
    def get_std_library_names() -> list:
        dotfile = f'{Path().home()}/.fmp'
        if Path(dotfile).exists():
            with open(dotfile) as j:
                loaded_dotfile = json.load(j)
                if [*sys.version_info][:3] == loaded_dotfile[0]:
                    return loaded_dotfile[1]
        result = requests.get(
            'https://github.com/python/cpython/tree/main/Doc/library')
        soup = BeautifulSoup(result.text, features='html.parser')
        rst_files = soup.find_all(title=re.compile(r'\.rst$'))
        names = [i.extract().get_text() for i in rst_files]
        std_lib_names = []
        for name in names:
            if name.endswith('.rst') and not any(x in name
                                                 for x in [' ', '-']):
                std_lib_names.append(name.split('.')[0])
        std_lib_names_list = list(set(std_lib_names))
        with open(dotfile, 'w') as j:
            json.dump([[*sys.version_info][:3], std_lib_names_list], j)
        return std_lib_names_list

    def sort_imports(self, file_path: str) -> list:
        with tempfile.NamedTemporaryFile() as fp:
            with open(file_path, 'rb') as f:
                fp.write(f.read())
            fp.seek(0)
            if self.keep_external_unused_imports:
                options = ['--in-place', '--ignore-init-module-imports']
            else:
                options = [
                    '--remove-all-unused-imports',
                    '--ignore-init-module-imports', '--in-place'
                ]
            if not self.keep_unused_imports:
                _main([None, *options, fp.name],
                      standard_out=sys.stdout,
                      standard_error=sys.stderr)
            lines = [x.decode() for x in fp.readlines()]

        imports = collections.defaultdict(list)
        non_imports = []
        top_lines = []
        std_lib_names = self.get_std_library_names()
        imports_start = False

        for line in lines:
            multi_lines_import = False
            valid_import = None

            if line.startswith('import '):
                imports_start = True
                module_name = line.split('import ')[1].strip().replace(
                    '\n', '')
            elif line.startswith('from ') and ' import ' in line:
                imports_start = True
                module_name = line.split('from')[1].split('import')[0].strip()
                if '(' in line or '\\' in line:
                    multi_lines_import = True
            elif not imports_start:
                if not self.only_imports:
                    top_lines.append(line)
                continue
            else:
                if not self.only_imports:
                    non_imports.append(line)
                continue

            if multi_lines_import:
                next_line_idx = lines.index(line) + 1
                next_line = lines[next_line_idx]
                lines.remove(lines[next_line_idx])
                line = f'{line.strip()}\n{next_line}'
                lines[next_line_idx - 1] = line
            elif not multi_lines_import:
                line_body = ast.parse(line).body[0]
                valid_import = isinstance(line_body,
                                          (ast.ImportFrom, ast.Import))

            if ('.' in module_name and 'from .' not in line
                    and module_name.split('.')[0] not in std_lib_names):
                _module_name = module_name.split('.')[0]
                grandparent = Path('/'.join(file_path.split('/')[:-1]))
                grand_grandparent = Path('/'.join(file_path.split('/')[:-2]))

                if Path(f'{Path(file_path).parent}/{_module_name}').is_dir(
                ) or (grandparent.is_dir() and grandparent.name == _module_name
                      ) or (grand_grandparent.is_dir()
                            and grand_grandparent.name == _module_name):
                    imports['partial_relative_imports'].append(line)

            if valid_import:
                sys.path.insert(0, str(Path(file_path).absolute().parent))
                try:
                    spec = importlib.util.find_spec(module_name)
                except ModuleNotFoundError:
                    spec = _DummySpecLoader()

                if module_name in std_lib_names or module_name.split(
                        '.')[0] in std_lib_names:
                    if line.startswith('import '):
                        imports['std_lib_imports'].append(line)
                    else:
                        imports['partial_std_lib_imports'].append(line)
                else:
                    if spec and spec.loader and (Path(
                            spec.loader.path).parent == Path(
                                Path(file_path).absolute()).parent):

                        if line.startswith('import '):
                            imports['relative_imports'].append(line)
                        elif line.startswith('from ') and ' import ' in line:
                            if ',' in line:
                                pimport_names = line.split('import ')[1]
                                pimport_names = pimport_names.replace(' ', '')
                                if multi_lines_import and '(' in pimport_names:
                                    pimport_names = pimport_names.split(',')
                                    pimport_names[0] = pimport_names[0][1:]
                                    pimport_names[-1] = pimport_names[-1][:-1]
                                    pimport_names = ', '.join(
                                        sorted(pimport_names))

                                elif (multi_lines_import
                                      and '\\' in pimport_names):
                                    pimport_names = pimport_names.replace(
                                        '\\', '')
                                    pimport_names = ', '.join(
                                        sorted(pimport_names.split(',')))

                                if multi_lines_import:
                                    pimport_names = '(' + pimport_names + ')'

                                line = \
                                f'from {module_name} import {pimport_names}'
                            imports['partial_relative_imports'].append(line)
                    else:
                        if line.startswith('import '):
                            imports['external_imports'].append(line)
                        elif line.startswith('from ') and ' import ' in line:
                            imports['partial_external_imports'].append(line)

        order = [
            'std_lib_imports', 'partial_std_lib_imports', 'external_imports',
            'partial_external_imports', 'relative_imports',
            'partial_relative_imports'
        ]
        imports_sorted = {k: sorted(list(set(imports[k]))) for k in order}
        duplicate_imports = []
        for _import in imports_sorted['partial_relative_imports']:
            if _import in imports_sorted['partial_external_imports']:
                duplicate_imports.append(_import)

        for _import in duplicate_imports:
            imports_sorted['partial_relative_imports'].remove(_import)

        vals = list(imports_sorted.values())

        out_file = []
        if not self.only_imports:
            out_file.append(top_lines + ['\n'])
        out_file.append(sum(vals[:2], []) + ['\n'])
        out_file.append(sum(vals[2:4], []) + ['\n'])
        out_file.append(sum(vals[4:], []) + ['\n'])
        if not self.only_imports:
            out_file.append(non_imports)
        return sum(out_file, [])

    def format(self, file_path: Union[list, str]) -> None:
        if isinstance(file_path, str):
            file_path = [file_path]

        for file in file_path:
            Console().rule(file)
            out_file = self.sort_imports(file)
            reformatted_code, _ = FormatCode(''.join(out_file),
                                             style_config=self.style)

            if self.in_place and self.only_imports:
                raise TypeError(
                    'Can\'t use `--only-imports` and `--in-place` together!')
            if self.in_place:
                with open(file, 'w') as f:
                    f.write(reformatted_code)
            else:
                console = Console()
                console.print(
                    Syntax(reformatted_code,
                           'python',
                           line_numbers=self.show_line_numbers,
                           theme='ansi_dark',
                           background_color='#282C34'))
            return reformatted_code
