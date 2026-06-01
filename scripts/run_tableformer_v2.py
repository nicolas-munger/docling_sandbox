from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableStructureV2Options,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption


def main() -> None:
    debug_dir = REPO_ROOT / "scratch" / "tableformer_v2_debug"
    settings.debug.visualize_tables = True
    settings.debug.debug_output_path = str(debug_dir)

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options = TableStructureV2Options()
    pipeline_options.do_ocr = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert("https://arxiv.org/pdf/2206.01062")
    print(f"Saved table debug images under: {debug_dir}")
    print(result.document.export_to_markdown())


if __name__ == "__main__":
    main()