#!/usr/bin/env python
# coding: utf-8

import argparse

from fmp.fmp import FormatPython


def opts() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='Files to format')
    parser.add_argument('-s',
                        '--style',
                        type=str,
                        choices=['pep8', 'google', 'yapf', 'facebook'],
                        default='pep8',
                        help='Formatting style')
    parser.add_argument('-i',
                        '--in-place',
                        help='Make changes in-place',
                        action='store_true')
    parser.add_argument('-o',
                        '--only-imports',
                        help='Only return sorted import statements',
                        action='store_true')
    parser.add_argument('-n',
                        '--show-line-numbers',
                        help='Render a column for line numbers',
                        action='store_true')
    parser.add_argument('-k',
                        '--keep-unused-imports',
                        help='Keep the import statement of all unused modules',
                        action='store_true')
    parser.add_argument(
        '-K',
        '--keep-external-unused-imports',
        help='Keep the import statement of external unused modules',
        action='store_true')
    return parser.parse_args()


def main():
    args = opts()
    fmp = FormatPython(
        only_imports=args.only_imports,
        in_place=args.in_place,
        show_line_numbers=args.show_line_numbers,
        style=args.style,
        keep_external_unused_imports=args.keep_external_unused_imports,
        keep_unused_imports=args.keep_unused_imports)
    fmp.format(file_path=args.files)
