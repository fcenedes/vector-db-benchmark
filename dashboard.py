#!/usr/bin/env python3
"""
Vector DB Benchmark Dashboard

A Dash-based dashboard for visualizing benchmark results.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd


def load_results(results_dir: str = "results/results") -> pd.DataFrame:
    """Load all benchmark results from JSON files into a DataFrame."""
    records = []
    
    for filepath in Path(results_dir).glob("*.json"):
        filename = filepath.name
        
        # Skip summary files for now - we'll use individual results
        if "summary" in filename:
            continue
            
        with open(filepath, "r") as f:
            data = json.load(f)
        
        params = data.get("params", {})
        results = data.get("results", {})
        
        record = {
            "filename": filename,
            "dataset": params.get("dataset", ""),
            "experiment": params.get("experiment", ""),
            "engine": params.get("engine", ""),
        }
        
        # Determine if this is a search or upload result
        if "search" in filename:
            record["type"] = "search"
            record["parallel"] = params.get("parallel", 1)
            record["search_ef"] = params.get("search_params", {}).get("ef", 0)
            record["rps"] = results.get("rps", 0)
            record["mean_time"] = results.get("mean_time", 0) * 1000  # Convert to ms
            record["p95_time"] = results.get("p95_time", 0) * 1000  # Convert to ms
            record["p99_time"] = results.get("p99_time", 0) * 1000  # Convert to ms
            record["mean_precisions"] = results.get("mean_precisions", 0)
        elif "upload" in filename:
            record["type"] = "upload"
            record["parallel"] = params.get("parallel", 1)
            record["upload_time"] = results.get("upload_time", 0)
            record["total_time"] = results.get("total_time", 0)
            memory_usage = results.get("memory_usage", {})
            used_memory = memory_usage.get("used_memory", [0])
            record["memory_gb"] = used_memory[0] / (1024 * 1024 * 1024) if used_memory else 0
        else:
            continue
            
        records.append(record)
    
    return pd.DataFrame(records)


def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
    """Get unique non-empty values from a column."""
    return sorted([v for v in df[column].unique() if v])


# Load data
df = load_results()

# Get unique values for dropdowns
datasets = get_unique_values(df, "dataset")
experiments = get_unique_values(df, "experiment")
parallel_values = sorted(df[df["type"] == "search"]["parallel"].unique())

# Metric options
METRIC_OPTIONS = [
    {"label": "Queries Per Second (RPS)", "value": "rps"},
    {"label": "Average Latency (ms)", "value": "mean_time"},
    {"label": "P95 Latency (ms)", "value": "p95_time"},
    {"label": "Index Build Time (s)", "value": "upload_time"},
    {"label": "Total Memory Usage (GB)", "value": "memory_gb"},
]

# Create a lookup dict for metric labels
METRIC_LABELS = {opt["value"]: opt["label"] for opt in METRIC_OPTIONS}

# Create Dash app
app = dash.Dash(__name__, title="Vector DB Benchmark Dashboard")

app.layout = html.Div([
    html.H1("Vector DB Benchmark Dashboard", style={"textAlign": "center"}),
    
    html.Div([
        html.Div([
            html.Label("Dataset:"),
            dcc.Dropdown(
                id="dataset-dropdown",
                options=[{"label": d, "value": d} for d in datasets],
                value=datasets[0] if datasets else None,
                clearable=False,
            ),
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Number of Clients (Parallel):"),
            dcc.Dropdown(
                id="parallel-dropdown",
                options=[{"label": str(p), "value": p} for p in parallel_values],
                value=parallel_values[0] if parallel_values else None,
                clearable=False,
            ),
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Metric:"),
            dcc.Dropdown(
                id="metric-dropdown",
                options=METRIC_OPTIONS,
                value="rps",
                clearable=False,
            ),
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
    ], style={"display": "flex", "justifyContent": "center"}),
    
    html.Div([
        dcc.Graph(id="benchmark-graph", style={"height": "70vh"}),
    ]),
    
    html.Div([
        html.P("Each point represents a configuration (build params + ef_search). Lines connect points from the same build config. Hover for details.",
               style={"textAlign": "center", "color": "gray"}),
    ]),
], style={"padding": "20px"})


@callback(
    Output("benchmark-graph", "figure"),
    [Input("dataset-dropdown", "value"),
     Input("parallel-dropdown", "value"),
     Input("metric-dropdown", "value")]
)
def update_graph(dataset: str, parallel: int, metric: str):
    """Update the graph based on selected filters."""
    if not dataset:
        return px.line(title="No data available")

    # Handle upload metrics separately (no precision axis)
    if metric in ["upload_time", "memory_gb"]:
        filtered_df = df[(df["dataset"] == dataset) & (df["type"] == "upload")]
        if filtered_df.empty:
            return px.bar(title=f"No upload data available for {dataset}")

        agg_df = filtered_df.groupby("experiment")[metric].mean().reset_index()

        fig = px.bar(
            agg_df,
            x="experiment",
            y=metric,
            color="experiment",
            title=f"{METRIC_LABELS[metric]} by Build Config",
            labels={"experiment": "Build Config", metric: METRIC_LABELS[metric]},
        )
        fig.update_layout(xaxis_tickangle=-45, showlegend=True, legend_title="Build Config")
        return fig

    # Search metrics - line chart with precision on X-axis
    filtered_df = df[
        (df["dataset"] == dataset) &
        (df["parallel"] == parallel) &
        (df["type"] == "search")
    ]
    if filtered_df.empty:
        return px.line(title=f"No search data for {dataset} with {parallel} clients")

    # Aggregate by experiment and search_ef (take mean of multiple runs)
    agg_df = filtered_df.groupby(["experiment", "search_ef"]).agg({
        "rps": "mean",
        "mean_precisions": "mean",
        "mean_time": "mean",
        "p95_time": "mean",
    }).reset_index()

    # Sort by precision for proper line drawing
    agg_df = agg_df.sort_values(["experiment", "mean_precisions"])

    fig = px.line(
        agg_df,
        x="mean_precisions",
        y=metric,
        color="experiment",
        markers=True,
        title=f"Precision vs {METRIC_LABELS[metric]} ({parallel} clients)",
        labels={
            "mean_precisions": "Precision",
            metric: METRIC_LABELS[metric],
            "experiment": "Build Config",
        },
        hover_data=["search_ef", "rps", "mean_time", "p95_time"],
    )

    fig.update_traces(marker=dict(size=10))

    fig.update_layout(
        showlegend=True,
        legend_title="Build Config",
        xaxis=dict(tickformat=".0%"),
    )

    return fig


if __name__ == "__main__":
    print("Starting Vector DB Benchmark Dashboard...")
    print(f"Loaded {len(df)} result records")
    print(f"Datasets: {datasets}")
    print(f"Experiments: {experiments}")
    print(f"Parallel values: {parallel_values}")
    app.run(debug=True, host="0.0.0.0", port=8050)

