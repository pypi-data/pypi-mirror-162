"""
MicroView module containing schemas for data validation
"""
from pathlib import Path

HERE = Path(__file__).parent.resolve()

contrast_table_schema = Path(HERE, "contrast_table.schema.json")
kaiju_report_schema = Path(HERE, "kaiju_report.schema.json")
