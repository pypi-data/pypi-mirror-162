from collections import Counter, defaultdict
from pathlib import Path
from typing import Counter, Dict, List, Tuple

import pandas as pd
from numpy import NaN, count_nonzero, log
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.stats.ordination import pcoa


def parse_reports(files: List[Path], report_type: str) -> dict:
    """
    Parse taxonomy results

    Args:
        files (list): List of file paths to read reports from
        report_type (str): String denoting report type, kaiju or kraken

    Returns:
        dict: Dict of each sample as key and every value differentiating
            assigned (and respective taxons) and unassigned read counts and
            percentages.

    """
    parsed_stats: Dict[str, dict] = {}

    for sample in files:
        df = pd.read_table(sample).replace({"None": NaN}, regex=True)

        sample_name = sample.name
        parsed_stats[sample_name] = defaultdict(lambda: {"n_reads": 0, "percent": 0})
        parsed_stats[sample_name].update({"assigned": {}})

        if report_type == "kaiju":
            parse_kaiju2table(sample_name, df, parsed_stats)
        elif report_type == "kraken":
            parse_kraken_report(sample_name, df, parsed_stats)

    return parsed_stats


def parse_kaiju2table(sample_name: str, df, parsed_stats: Dict) -> None:
    """
    Parses kaiju report
    """
    for row in df.itertuples():

        row_dict = {"n_reads": row.reads, "percent": row.percent}
        if row.taxon_name == "unclassified":
            parsed_stats[sample_name].update({"unclassified": row_dict})
        elif row.taxon_name.startswith("cannot"):
            parsed_stats[sample_name].update({"cannot be assigned": row_dict})
        else:
            taxon_name: str = list(filter(None, row.taxon_name.split(";")))[-1]
            parsed_stats[sample_name]["assigned"][taxon_name] = row_dict


def parse_kraken_report(sample_name: str, df, parsed_stats: Dict) -> None:
    """
    Parse Kraken-style report
    """
    df.columns = [
        "percent",
        "reads_root",
        "reads",
        "rank_code",
        "taxid",
        "taxon_name",
    ]

    for row in df.itertuples():
        row_dict = {"n_reads": row.reads, "percent": row.percent}
        if row.rank_code == "U":
            parsed_stats[sample_name].update({"unclassified": row_dict})
        else:
            if row.reads > 0:
                taxon_name = row.taxon_name.strip()
                parsed_stats[sample_name]["assigned"][taxon_name] = row_dict


def get_taxon_counts(samples_stats: Dict) -> Dict:
    """
    Agreggates taxon counts across all samples into single Counter

    Args:
        samples_stats (dict): Dict resulting from
            microview.parse_taxonomy.parse_reports

    Returns:
        Counter: Counter containing agreggated read counts across all samples

    """
    all_sample_counts: Dict = {}

    for sample, data in samples_stats.items():
        all_sample_counts[sample] = Counter()
        for category, cat_data in data.items():
            if category == "assigned":
                for tax_name, info in cat_data.items():
                    all_sample_counts[sample][tax_name] += info["n_reads"]
            else:
                all_sample_counts[sample][category] += cat_data["n_reads"]

    return all_sample_counts


def get_read_assignment(parsed_stats: Dict) -> Dict:
    """
    Get number of assigned/unassigned reads for each sample

    Args:
        parsed_stats (dict): Dict result from
            microview.parse_taxonomy.parse_reports

    Returns:
        dict: Dict differentiating assigned / unassigned number of reads
            for each sample.
    """
    results: Dict[str, dict] = {}
    for sample_name, _ in parsed_stats.items():
        results[sample_name] = {"assigned": 0, "unassigned": 0}
        assigned = sum(
            d["n_reads"] for d in parsed_stats[sample_name]["assigned"].values()
        )

        unassigned = (
            parsed_stats[sample_name]["cannot be assigned"]["n_reads"]
            + parsed_stats[sample_name]["unclassified"]["n_reads"]
        )

        total = assigned + unassigned
        results[sample_name]["assigned"] = (assigned / total) * 100
        results[sample_name]["unassigned"] = (unassigned / total) * 100

    return results


def get_common_taxas(sample_counts: Dict) -> Dict:
    """
    Get 5 most common taxas for each sample

    Args:
        sample_counts (dict): Dict resulting from
            microview.parse_taxonomy.get_taxon_counts

    Returns:
        dict: Dict with 5 most common taxons for each sample
            plus an 'other' key agreggating other taxon counts.
    """
    most_common: Dict = {}
    for sample in sample_counts.keys():
        sample_total = sum(sample_counts[sample].values())
        most_common_vals = sample_counts[sample].most_common(5)
        other = sample_total - sum(v for _, v in most_common_vals)
        most_common[sample] = {
            k: round((v / sample_total) * 100, 2) for k, v in most_common_vals
        }
        most_common[sample]["other"] = (other / sample_total) * 100
    return most_common


def calculate_abund_diver(sample_counts: Dict) -> Tuple[pd.DataFrame]:
    """
    Calculate alpha diversity, beta diversity and pielou evenness in samples

    Args:
        sample_counts (dict): Dict resulting from
            microview.parse_taxonomy.get_taxon_counts

    Returns:
        tuple: Two dataframes, first one containing sample name,
            number of taxas, alpha diversity and Pielou's evenness;
            Second one containing a PCoA of the beta diversity result.
    """
    taxa_counts_df = pd.DataFrame(sample_counts).T.fillna(0)
    ids = taxa_counts_df.index

    shannon_div = alpha_diversity("shannon", taxa_counts_df.to_numpy(), ids)

    div_abund_df = pd.DataFrame(
        shannon_div, columns=["Shannon Diversity"]
    ).reset_index()

    div_abund_df["N Taxas"] = count_nonzero(taxa_counts_df.to_numpy(), axis=1)

    # Pielou's evenness = diversity divided by the log specnumber
    div_abund_df["Pielou Evenness"] = div_abund_df["Shannon Diversity"] / log(
        div_abund_df["N Taxas"]
    )

    # Beta diversity analysis

    beta_div = beta_diversity(
        metric="braycurtis", counts=taxa_counts_df.to_numpy(), ids=ids, validate=True
    )

    betadiv_pcoa = pcoa(beta_div)

    return div_abund_df, betadiv_pcoa


def get_tax_data(paths: List[Path], report_type: str) -> Dict:
    """
    Master function for generating stats from taxonomic classification results

    This function handles parsing reports, agreggating taxon counts, generating
    read assignment statistics and, most importantly, generating diversity and
    abundance metrics.

    Args:
        paths (list): List of paths of where to read the reports from
        report_type (str): Detected report type, kaiju or kraken.

    Returns:
        dict: Dict with 4 keys: 'sample n reads' containing read assignment stats;
            'common taxas' containing the 5 most common taxas and their respective
            counts in each sample; 'abund and div' containing abundance and diversity
            metrics; and 'beta div' containing a PCoA of beta diversity results.
    """

    parsed_stats = parse_reports(paths, report_type)

    all_sample_counts = get_taxon_counts(parsed_stats)

    n_reads = get_read_assignment(parsed_stats)

    most_common = get_common_taxas(all_sample_counts)

    abund_div_df, betadiv_pcoa = calculate_abund_diver(all_sample_counts)

    stats_df = pd.DataFrame(n_reads).T.reset_index().melt(id_vars=["index"])

    most_common_df = (
        pd.DataFrame.from_dict(most_common, orient="index")
        .reset_index()
        .melt(id_vars=["index"])
        .sort_values(["index", "variable"], ascending=False)
    )

    return {
        "sample n reads": stats_df,
        "common taxas": most_common_df,
        "abund and div": abund_div_df,
        "beta div": betadiv_pcoa,
    }
