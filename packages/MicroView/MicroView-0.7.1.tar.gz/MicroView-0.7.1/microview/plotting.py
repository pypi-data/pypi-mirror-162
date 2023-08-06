from typing import Dict, Optional

import plotly.express as px
from plotly import io
from plotly.graph_objects import Figure


def export_to_html(fig: Figure, div_id: str) -> str:
    """
    Export plotly graph to html format

    Args:
        fig (Figure): Plotly figure to export
        div_id (str): String to use as the plot's div id.

    Returns:
        str: HTML string with plot
    """
    return io.to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,
        include_mathjax=False,
        div_id=div_id,
    )


def merge_with_contrasts(df, contrast_df, left_colname: Optional[str] = "index"):
    """
    Merges a dataframe with the dataframe containing contrasts (or groups)
    """
    merged_df = df.merge(
        contrast_df, left_on=left_colname, right_on="sample", how="left"
    )

    return merged_df


def plot_common_taxas(common_taxas_df, **kwargs):
    """
    Generate bar plot with most common taxas
    """
    return px.bar(
        common_taxas_df.sort_values(by=["value", "variable"], ascending=[False, True]),
        x="index",
        y="value",
        color="variable",
        **kwargs,
    )


def plot_abund_div(abund_div_df, **kwargs):
    """
    Generate scatter plot of Pielou's Evenness and Shannon's Diversity (alpha)
    """
    return px.scatter(
        abund_div_df,
        x="Pielou Evenness",
        y="Shannon Diversity",
        size="N Taxas",
        hover_data=["index"],
        **kwargs,
    )


def plot_beta_pcoa(beta_pcoa, **kwargs):
    """
    Generate scatter plot of two first coordinates of Beta Diversity PCoA
    """
    return px.scatter(beta_pcoa, x="PC1", y="PC2", hover_data=["sample"], **kwargs)


def generate_taxo_plots(tax_data: Dict, contrast_df=None) -> Dict:
    """
    Get all taxonomy plots

    Master function to generate all plots to be used in the final report.

    Args:
        tax_data (dict): Dict resulting from
            microview.parse_taxonomy.get_tax_data
        contrast_df (pd.DataFrame): Dataframe with sample names and
            contrasts, if available.

    Returns:
        dict: Dict containing all plots, one for each key.
    """
    assigned = px.bar(
        tax_data["sample n reads"], x="index", y="value", color="variable"
    )

    assigned.update_layout(
        xaxis={"categoryorder": "category ascending"},
    )

    assigned_html = export_to_html(assigned, "assigned-plot")

    # Beta diversity plots

    pcoa_embed = (
        tax_data["beta div"].samples[["PC1", "PC2"]].rename_axis("sample").reset_index()
    )
    var_explained = (
        tax_data["beta div"]
        .proportion_explained[:9]
        .to_frame(name="variance explained")
        .reset_index()
        .rename(columns={"index": "PC"})
    )

    pcoa_var = px.line(var_explained, x="PC", y="variance explained", text="PC")
    pcoa_var.update_traces(textposition="bottom right")

    if contrast_df is not None and "group" in contrast_df.columns:
        merged_taxas_df = merge_with_contrasts(tax_data["common taxas"], contrast_df)

        common_taxas = plot_common_taxas(merged_taxas_df, facet_col="group")
        common_taxas.update_xaxes(matches=None)

        abund_div = plot_abund_div(
            merge_with_contrasts(tax_data["abund and div"], contrast_df),
            color="group",
        )

        betadiv_pcoa = plot_beta_pcoa(
            merge_with_contrasts(pcoa_embed, contrast_df, left_colname="sample"),
            color="group",
        )

    else:
        common_taxas = plot_common_taxas(tax_data["common taxas"])

        abund_div = plot_abund_div(tax_data["abund and div"])

        betadiv_pcoa = plot_beta_pcoa(pcoa_embed)

    common_taxas.update_traces(showlegend=False)
    common_taxas.update_layout(
        xaxis={"categoryorder": "category ascending"},
    )

    common_taxas_html = export_to_html(common_taxas, "taxas-plot")

    abund_div_html = export_to_html(abund_div, "abund-div-plot")

    pcoa_var_html = export_to_html(pcoa_var, "pcoa-explained-variance")

    betadiv_pcoa_html = export_to_html(betadiv_pcoa, "betadiv_pcoa")

    return {
        "assigned_plot": assigned_html,
        "common_taxas_plot": common_taxas_html,
        "abund_div_plot": abund_div_html,
        "pcoa_var_plot": pcoa_var_html,
        "beta_div_pcoa": betadiv_pcoa_html,
    }
