from pathlib import Path

import rich_click as click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from rich.console import Console

from microview import __version__ as mv_version
from microview.file_finder import find_reports, parse_source_table
from microview.parse_taxonomy import get_tax_data
from microview.plotting import generate_taxo_plots
from microview.rendering import render_base


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@optgroup.group(
    "Input data source",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="Input data source",
)
@optgroup.option(
    "-t",
    "--taxonomy",
    type=click.Path(path_type=Path),
    help="Path to taxonomy classification results",
)
@optgroup.option(
    "-df",
    "--csv-file",
    type=click.Path(path_type=Path),
    help="2-column CSV table (sample,group) with taxonomy classification results paths",
)
@click.option(
    "-o",
    "--output",
    default="microview_report.html",
    help="Report file name",
    type=click.Path(path_type=Path, writable=True, resolve_path=True),
)
def main(taxonomy: Path, csv_file: Path, output: Path) -> None:
    """
    MicroView, a reporting tool for taxonomic classification

    MicroView agreggates reports from taxonomic classification tools,
    such as Kaiju and Kraken.

    You can provide either a path to results
    in the -t argument or, with -df, a path to a 2-column CSV file,
    the first column sample paths and the second containing group names
    or contrasts.
    """

    console = Console(stderr=True, highlight=False)
    console.print(
        f"\n [bold]Running [blue]Micro[/][red]View[/] :glasses: [dim]v{mv_version}[/] \n"
    )
    data_source = taxonomy if taxonomy else csv_file

    with console.status("[bold]Reading report...[/]"):
        if csv_file is not None:
            parsed_result = parse_source_table(data_source, console)
            reports = parsed_result["paths"]
            report_type = parsed_result["report_type"]
        else:
            reports, report_type = find_reports(data_source, console)
            parsed_result = None

    try:
        console.print(
            f"\n Found [bold]{len(reports)}[/] {report_type.title()} reports... \n"
        )
        with console.status("[bold]Calculating metrics...[/]"):
            tax_results = get_tax_data(reports, report_type)
            # TODO: Improve this double check
            if parsed_result is not None:
                tax_plots = generate_taxo_plots(tax_results, parsed_result["dataframe"])
            else:
                tax_plots = generate_taxo_plots(tax_results)
            render_base(tax_plots=tax_plots, dir_path=data_source, output_path=output)
        console.print(f"\n Done!\n", style="bold green")
    except Exception:
        console.print_exception(show_locals=True)
