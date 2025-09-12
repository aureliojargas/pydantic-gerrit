"""
Script to auto-generate TypedDicts from Pydantic v2 models in a module.

Usage:
    python generate_typeddicts.py your_module.ModelName ...

This will print TypedDict definitions for the given models.
"""

import importlib
import pathlib
import sys
import json
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel


def python_type_to_typeddict(t: Any) -> str:
    # Handles basic types, generics, and nested models
    origin = get_origin(t)
    if origin is None:
        if isinstance(t, type) and issubclass(t, BaseModel):
            return f'"{t.__name__}Dict"'
        if t is type(None):
            return 'None'
        if hasattr(t, '__name__'):
            return t.__name__
        return str(t)
    if origin is list:
        return f'list[{python_type_to_typeddict(get_args(t)[0])}]'
    if origin is dict:
        k, v = get_args(t)
        return f'dict[{python_type_to_typeddict(k)}, {python_type_to_typeddict(v)}]'
    if origin is tuple:
        args = ', '.join(python_type_to_typeddict(a) for a in get_args(t))
        return f'tuple[{args}]'
    if origin is set:
        return f'set[{python_type_to_typeddict(get_args(t)[0])}]'
    if origin is type(None):
        return 'None'
    if origin is Union:
        args = get_args(t)
        return ' | '.join(python_type_to_typeddict(a) for a in args)
    return str(t)


def model_to_typeddict(model: type[BaseModel]) -> str:
    lines = [f'class {model.__name__}Dict(TypedDict, total=False):']
    for name, field in model.model_fields.items():
        typ = python_type_to_typeddict(field.annotation)
        lines.append(f'    {name}: {typ}')
    return '\n'.join(lines)


def main() -> None:
    print('from typing import TypedDict\n')
    for arg in sys.argv[1:]:
        if '.' not in arg:
            print(f'# Skipping {arg}: must be in module.ModelName format')
            continue
        module_name, class_name = arg.rsplit('.', 1)
        mod = importlib.import_module(module_name)
        model = getattr(mod, class_name)

        output_file = pathlib.Path(arg).with_suffix('.json')
        output_file.write_text(json.dumps(model.model_json_schema(), indent=2))
        print('Wrote schema to', output_file)

        # print(model_to_typeddict(model))
        # print()


if __name__ == '__main__':
    main()
