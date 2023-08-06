from pathlib import Path
from typing import Dict, List, Tuple

from frictionless import checks, validate
from pandas import read_csv

from microview.schemas import contrast_table_schema, kaiju_report_schema


def get_validation_dict(table: Path, **kwargs) -> Dict:
    """
    Validate data against checks or schema

    Args:
        table (Path): Path to tabular data to validate
        **kwargs (**kwargs): Other arguments, like a checklist or a schema

    Returns:
        dict: Dictionary containing three keys: 'report', for the report path
            itself; 'errors', with the number of errors; and 'error_messages', a
            list containing error codes and their respective messages
    """
    report = validate(
        table,
        **kwargs,
    )

    return {
        "report": table,
        "errors": report["stats"]["errors"],
        "error_messages": report.flatten(["code", "message"]),
    }


def is_kraken_report(report: Dict) -> bool:
    """
    Check if validation report corresponds to accurate Kraken result

    Args:
        report (dict): A dictionary output from
            microview.file_finder.get_validation_dict

    Returns:
        bool: True if report, False if not.
    """
    if report["errors"] == 0 or all(
        report_error[0] == "duplicate-label"
        for report_error in report["error_messages"]
    ):
        return True
    return False


def check_source_table_validation(report: Dict, console) -> None:
    """
    Check if source table validation didn't raise errors

    Args:
        report (dict): A result dictionary from
            microview.file_finder.get_validation_dict
        console (rich.Console): Console to print the outputs to

    """
    if report["errors"] > 0:
        console.print(
            " Source table does not follow expected 'sample,group' schema\n"
            " See the following errors raised during validation:",
            style="bold",
        )
        for error in report["error_messages"]:
            console.print(f" [red][bold]{error[0]}[/]: {error[1]}[/]")
        raise Exception("Source table does not follow schema")


def detect_report_type(report_paths: List[Path], console) -> Tuple[List[Path], str]:
    """
    Detect report type from file paths

    Validates tables present in report_paths against schemas or
    custom checks, inferring the type of report (kaiju or kraken).

    Args:
        report_paths (list): A list containing all report paths to validate.
        console (rich.Console): Console to print messages to

    Returns:
        tuple: First element the list of paths that pass the schema,
            second element the report type in string form.
    """
    kaiju_validated = [
        get_validation_dict(report, schema=kaiju_report_schema)
        for report in report_paths
    ]
    kaiju_reports = [
        kaiju_report["report"]
        for kaiju_report in kaiju_validated
        if kaiju_report["errors"] == 0
    ]
    if len(kaiju_reports) == 0:

        # TODO: Improve Kraken validation
        kraken_validated = [
            get_validation_dict(report, checks=[checks.table_dimensions(num_fields=6)])
            for report in report_paths
        ]
        kraken_reports = [
            kraken_report["report"]
            for kraken_report in kraken_validated
            if is_kraken_report(kraken_report)
        ]

        if len(kraken_reports) == 0:
            console.print("\n Could not find any valid reports", style="red")
            raise Exception("Could not find any valid files.")
        else:
            report_type = "kraken"
            return kraken_reports, report_type
    else:
        report_type = "kaiju"
        return kaiju_reports, report_type


def find_reports(reports_path: Path, console) -> Tuple[List[Path], str]:
    """
    Find reports in given path

    Args:
        reports_path (Path): Path to find the reports from
        console (rich.Console): Console to print messages to

    Returns:
        tuple: First element the list of report_paths validated against
            schemas or checks and second element the type detected from
            said paths.
    """
    file_paths: List[Path] = list(reports_path.glob("*tsv"))
    report_paths, report_type = detect_report_type(file_paths, console)
    return report_paths, report_type


def validate_paths(sample_paths: List[Path], source_table: Path) -> List[Path]:
    """
    Check if paths in source table are real paths and readable

    Args:
        sample_paths (list): List of paths to validate
        source_table (path): Path to source table

    Returns:
        list: A list containing the paths, now validated.
    """
    if all(sample_path.exists() for sample_path in sample_paths) != True:
        full_sample_paths: List[Path] = [
            source_table.parent.resolve().joinpath(sample) for sample in sample_paths
        ]

        if all(full_path.exists() for full_path in full_sample_paths) != True:
            raise Exception("One or more sample paths provided don't exist")

        return full_sample_paths

    return sample_paths


def parse_source_table(source_table: Path, console) -> Dict:
    """
    Parses source tables

    Validates tables and samples against checks and schemas, reads
    in the source table itself and returns a dict with a list of
    validated reports, the report type detected and the source table
    itself, in a pandas DataFrame.

    Args:
        source_table (Path): Path to the csv source table
        console (rich.Console): Console to print messages to, utilized by subfunctions.

    Returns:
        dict: Dict with 'paths', containing the report paths; 'report_type',
            with the detected report type; and 'dataframe' with the source
            table itself.
    """
    report = get_validation_dict(source_table, schema=contrast_table_schema)

    check_source_table_validation(report, console)

    df = read_csv(source_table)

    sample_paths: List[Path] = [Path(sample) for sample in df["sample"].to_list()]

    validated_paths = validate_paths(sample_paths, source_table)

    report_paths, report_type = detect_report_type(validated_paths, console)

    return {
        "paths": report_paths,
        "report_type": report_type,
        "dataframe": df,
    }
