"""Generate Python models from JSON Schema files."""

import json
import logging
from pathlib import Path
from typing import Literal

from datamodel_code_generator import DataModelType, InputFileType, PythonVersion, generate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ModelType = Literal[
    DataModelType.PydanticV2BaseModel,
    DataModelType.DataclassesDataclass,
    DataModelType.TypingTypedDict,
]
FORMAT_TO_DIR = {
    DataModelType.PydanticV2BaseModel: 'pydantic',
    DataModelType.DataclassesDataclass: 'dataclass',
    DataModelType.TypingTypedDict: 'typeddict',
}


def generate_models(
    version: str,
    model_type: ModelType = DataModelType.PydanticV2BaseModel,
    base_class: str | None = None,
) -> None:
    """Generate Python models from JSON Schema files.

    Args:
        version: Gerrit version (e.g., "3_12")
        model_type: Type of models to generate ("pydantic"/"dataclasses"/"typing")
        base_class: Optional base class for the models
    """
    schema_dir = Path('schemas') / f'v{version}'
    output_dir = Path('generated') / FORMAT_TO_DIR[model_type] / f'v{version}'

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    (output_dir / '__init__.py').touch()

    # Process each schema file
    for schema_file in schema_dir.glob('*.json'):
        output_file = output_dir / f'{schema_file.stem}.py'
        logger.info('Generating %s from %s', output_file, schema_file)

        # Add Python-specific metadata to schema
        with schema_file.open() as f:
            schema = json.load(f)
            # Add base class if specified
            if base_class:
                schema['$defs'] = schema.get('$defs', {})
                schema['$defs']['baseModel'] = {'type': 'object'}
                schema['allOf'] = [{'$ref': '#/$defs/baseModel'}]

        # Generate models
        generate(
            json.dumps(schema),  # Pass modified schema as string
            input_file_type=InputFileType.JsonSchema,
            input_filename=str(schema_file),
            output_model_type=model_type,
            output=output_file,
            use_double_quotes=False,  # Match our ruff config
            use_standard_collections=True,  # Use list/dict instead of List/Dict
            use_schema_description=True,
            field_constraints=True,
            snake_case_field=False,  # Preserve original field names
            strip_default_none=True,
            target_python_version=PythonVersion.PY_310,
            # base_class=base_class,
        )


def create_latest_symlinks() -> None:
    """Create 'latest' symlinks pointing to the newest version."""
    versions = sorted(
        (p.name[1:] for p in Path('schemas').glob('v*')),
        key=lambda v: [int(x) for x in v.split('_')],
        reverse=True,
    )
    if not versions:
        return

    latest = versions[0]
    for output_dir in FORMAT_TO_DIR.values():
        latest_link = Path('generated') / output_dir / 'latest'
        target = f'v{latest}'

        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(target, target_is_directory=True)


def main() -> None:
    """Generate all model types for all versions."""
    versions = [p.name[1:] for p in Path('schemas').glob('v*')]
    if not versions:
        logger.warning('No schema versions found in schemas/ directory')
        return

    for version in versions:
        generate_models(version, DataModelType.PydanticV2BaseModel)
        generate_models(version, DataModelType.DataclassesDataclass)
        generate_models(version, DataModelType.TypingTypedDict)

    create_latest_symlinks()


if __name__ == '__main__':
    main()
