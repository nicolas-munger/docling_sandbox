from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableStructureOptions,
    TableStructureV2Options,
)
from docling.datamodel.settings import settings
from docling.document_converter import (
    DocumentConverter,
    ImageFormatOption,
    PdfFormatOption,
)


DEFAULT_INPUT = "https://arxiv.org/pdf/2206.01062"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / "tableformer_compare"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Docling with TableFormer V1 and V2 on the same PDF or image for comparison."
    )
    parser.add_argument(
        "input_source",
        nargs="?",
        default=DEFAULT_INPUT,
        help="PDF or image path/URL to convert.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where comparison outputs will be written.",
    )
    return parser.parse_args()


def detect_input_format(input_source: str) -> InputFormat:
    parsed = urlparse(input_source)
    suffix = Path(parsed.path if parsed.scheme else input_source).suffix.lower()

    if suffix == ".pdf":
        return InputFormat.PDF
    if suffix in {".png", ".jpg", ".jpeg"}:
        return InputFormat.IMAGE

    raise ValueError(
        "Unsupported input type. Expected a .pdf, .png, .jpg, or .jpeg file."
    )


def get_input_name(input_source: str) -> str:
    parsed = urlparse(input_source)
    source_path = Path(parsed.path if parsed.scheme else input_source)
    return source_path.stem or "comparison"


def run_conversion(
    input_source: str,
    case_output_dir: Path,
    label: str,
    table_structure_options: TableStructureOptions | TableStructureV2Options,
) -> Path:
    debug_dir = case_output_dir / "DEBUG"
    markdown_path = case_output_dir / "MD" / f"md_{label}.md"

    debug_dir.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    settings.debug.visualize_tables = True
    settings.debug.debug_output_path = str(debug_dir)

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options = cast(object, table_structure_options)
    pipeline_options.do_ocr = True

    input_format = detect_input_format(input_source)
    format_option = (
        PdfFormatOption(pipeline_options=pipeline_options)
        if input_format == InputFormat.PDF
        else ImageFormatOption(pipeline_options=pipeline_options)
    )

    converter = DocumentConverter(
        format_options={input_format: format_option}
    )

    result = converter.convert(input_source)
    markdown_path.write_text(result.document.export_to_markdown(), encoding="utf-8")

    print(f"[{label}] Saved markdown to: {markdown_path}")
    print(f"[{label}] Saved table debug images under: {debug_dir}")
    print(f"[{label}] Markdown tail:\n{result.document.export_to_markdown()[-1000:]}")

    return markdown_path


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    case_output_dir = output_dir / get_input_name(args.input_source)

    case_output_dir.mkdir(parents=True, exist_ok=True)

    v1_markdown = run_conversion(
        input_source=args.input_source,
        case_output_dir=case_output_dir,
        label="v1",
        table_structure_options=TableStructureOptions(),
    )
    v2_markdown = run_conversion(
        input_source=args.input_source,
        case_output_dir=case_output_dir,
        label="v2",
        table_structure_options=TableStructureV2Options(),
    )

    print("\nComparison outputs:")
    print(f"- V1 markdown: {v1_markdown}")
    print(f"- V2 markdown: {v2_markdown}")
    print(f"- Case output directory: {case_output_dir}")


if __name__ == "__main__":
    main()