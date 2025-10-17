"""
Generate reports from transform output files.

This script auto-discovers output files and generates summary reports.
Supports multiple transforms by processing all *_nodes.tsv and *_edges.tsv files.
"""

import sys
from pathlib import Path
from typing import List, Tuple

import duckdb


def discover_output_files(output_dir: Path = Path("output")) -> List[Tuple[str, Path | None, Path | None]]:
    """
    Discover transform output files and group them by ingest name.

    Returns:
        List of tuples (ingest_name, nodes_file, edges_file)
    """
    if not output_dir.exists():
        print(f"Output directory {output_dir} does not exist")
        return []

    # Find all nodes and edges files
    nodes_files = list(output_dir.glob("*_nodes.tsv"))
    edges_files = list(output_dir.glob("*_edges.tsv"))

    # Track discovered transforms by name
    discovered_dict = {}

    # Process nodes files
    for nodes_file in nodes_files:
        ingest_name = nodes_file.stem.replace("_nodes", "")
        discovered_dict[ingest_name] = (nodes_file, None)

    # Process edges files
    for edges_file in edges_files:
        ingest_name = edges_file.stem.replace("_edges", "")
        if ingest_name in discovered_dict:
            # Update existing entry with edges file
            nodes_file, _ = discovered_dict[ingest_name]
            discovered_dict[ingest_name] = (nodes_file, edges_file)
        else:
            # Create new entry for edges-only transform
            discovered_dict[ingest_name] = (None, edges_file)

    # Convert dict to list of tuples
    return [(name, nodes, edges) for name, (nodes, edges) in discovered_dict.items()]


def generate_nodes_report(ingest_name: str, nodes_file: Path | None) -> None:
    """Generate nodes summary report."""
    if not nodes_file or not nodes_file.exists():
        print(f"Nodes file {nodes_file} does not exist, skipping")
        return
    
    output_file = nodes_file.parent / f"{ingest_name}_nodes_report.tsv"
    
    query = f"""
    SELECT category, split_part(id, ':', 1) as prefix, count(*)
    FROM '{nodes_file}'
    GROUP BY all
    ORDER BY all
    """
    
    try:
        duckdb.sql(f"copy ({query}) to '{output_file}' (header, delimiter '\\t')")
        print(f"Generated nodes report: {output_file}")
    except Exception as e:
        print(f"Error generating nodes report for {ingest_name}: {e}")


def generate_edges_report(ingest_name: str, edges_file: Path | None) -> None:
    """Generate edges summary report."""
    if not edges_file or not edges_file.exists():
        print(f"Edges file {edges_file} does not exist, skipping")
        return
    
    output_file = edges_file.parent / f"{ingest_name}_edges_report.tsv"
    
    query = f"""
    SELECT category, split_part(subject, ':', 1) as subject_prefix, predicate,
    split_part(object, ':', 1) as object_prefix, count(*)
    FROM '{edges_file}'
    GROUP BY all
    ORDER BY all
    """
    
    try:
        duckdb.sql(f"copy ({query}) to '{output_file}' (header, delimiter '\\t')")
        print(f"Generated edges report: {output_file}")
    except Exception as e:
        print(f"Error generating edges report for {ingest_name}: {e}")


def main():
    """Main entry point for report generation."""
    output_dir = Path("output")
    
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    print(f"Discovering output files in {output_dir}")
    discovered_files = discover_output_files(output_dir)
    
    if not discovered_files:
        print("No transform output files found")
        return
    
    print(f"Found {len(discovered_files)} transform output(s)")
    
    for ingest_name, nodes_file, edges_file in discovered_files:
        print(f"Processing {ingest_name}...")
        generate_nodes_report(ingest_name, nodes_file)
        generate_edges_report(ingest_name, edges_file)
    
    print("Report generation complete")


if __name__ == "__main__":
    main()