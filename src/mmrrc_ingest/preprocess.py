"""
Preprocessing script for MMRRC catalog data using DuckDB.

This script normalizes the denormalized MMRRC catalog CSV into three separate files:
1. genotypes.csv - One row per unique genotype
2. genotype_to_phenotype.csv - One row per genotype-phenotype association
3. allele_to_genotype.csv - One row per allele-genotype association
"""

from pathlib import Path

import duckdb


def preprocess_mmrrc(input_file: Path, output_dir: Path) -> None:
    """Preprocess MMRRC catalog data into normalized CSV files using DuckDB."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {input_file} into DuckDB...")
    con = duckdb.connect(":memory:")

    # Load the CSV file, treating all columns as VARCHAR to avoid type issues
    con.execute(f"""
        CREATE TABLE mmrrc AS
        SELECT * FROM read_csv_auto('{input_file}', all_varchar=true)
    """)  # noqa: S608

    # Get row count
    result = con.execute("SELECT COUNT(*) FROM mmrrc").fetchone()
    total_rows = result[0] if result else 0
    print(f"Loaded {total_rows} rows")

    # 1. Create genotypes.csv - one row per unique STRAIN/STOCK_ID
    print("\nCreating genotypes.csv...")
    genotypes_file = output_dir / "genotypes.csv"

    con.execute(f"""
        COPY (
            SELECT DISTINCT
                "STRAIN/STOCK_ID" as strain_id,
                FIRST("STRAIN/STOCK_DESIGNATION") as strain_designation,
                FIRST(OTHER_NAMES) as other_names,
                FIRST(STRAIN_TYPE) as strain_type,
                FIRST(STATE) as state,
                FIRST(MUTATION_TYPE) as mutation_type,
                FIRST(CHROMOSOME) as chromosome,
                FIRST(SDS_URL) as sds_url,
                FIRST(ACCEPTED_DATE) as accepted_date,
                FIRST(RESEARCH_AREAS) as research_areas,
                FIRST(PUBMED_IDS) as pubmed_ids,
                FIRST(MPT_IDS) as mpt_ids_raw
            FROM mmrrc
            GROUP BY "STRAIN/STOCK_ID"
            ORDER BY "STRAIN/STOCK_ID"
        ) TO '{genotypes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608

    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{genotypes_file}')").fetchone()  # noqa: S608
    genotype_count = result[0] if result else 0
    print(f"  Wrote {genotype_count} unique genotypes")

    # 2. Create allele_to_genotype.csv - one row per allele-genotype pair
    print("\nCreating allele_to_genotype.csv...")
    allele_genotypes_file = output_dir / "allele_to_genotype.csv"

    con.execute(f"""
        COPY (
            SELECT DISTINCT
                MGI_ALLELE_ACCESSION_ID as allele_id,
                ALLELE_SYMBOL as allele_symbol,
                ALLELE_NAME as allele_name,
                "STRAIN/STOCK_ID" as strain_id,
                MUTATION_TYPE as mutation_type,
                CHROMOSOME as chromosome
            FROM mmrrc
            WHERE MGI_ALLELE_ACCESSION_ID IS NOT NULL
              AND MGI_ALLELE_ACCESSION_ID != ''
            ORDER BY "STRAIN/STOCK_ID", MGI_ALLELE_ACCESSION_ID
        ) TO '{allele_genotypes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608

    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{allele_genotypes_file}')").fetchone()  # noqa: S608
    allele_count = result[0] if result else 0
    print(f"  Wrote {allele_count} allele-genotype associations")

    # 3. Create genotype_to_phenotype.csv - explode MP IDs from MPT_IDS field
    print("\nCreating genotype_to_phenotype.csv...")
    genotype_phenotypes_file = output_dir / "genotype_to_phenotype.csv"

    # First, create a table with exploded MP IDs
    con.execute("""
        CREATE TABLE phenotype_associations AS
        SELECT DISTINCT
            "STRAIN/STOCK_ID" as strain_id,
            UNNEST(regexp_extract_all(MPT_IDS, 'MP:\\d+')) as mp_id,
            MPT_IDS as mpt_ids_raw
        FROM mmrrc
        WHERE MPT_IDS IS NOT NULL
          AND MPT_IDS != ''
          AND regexp_extract_all(MPT_IDS, 'MP:\\d+') IS NOT NULL
    """)

    # Now extract phenotype labels for each MP ID
    # We'll extract the text before each [MP:XXXXXX] pattern
    con.execute(f"""
        COPY (
            SELECT DISTINCT
                strain_id,
                mp_id as phenotype_id,
                regexp_extract(
                    mpt_ids_raw,
                    '([^|\\[]+)\\s*\\[' || mp_id || '\\]',
                    1
                ) as phenotype_label
            FROM phenotype_associations
            WHERE mp_id IS NOT NULL
            ORDER BY strain_id, mp_id
        ) TO '{genotype_phenotypes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608

    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{genotype_phenotypes_file}')").fetchone()  # noqa: S608
    phenotype_count = result[0] if result else 0
    print(f"  Wrote {phenotype_count} genotype-phenotype associations")

    print("\nPreprocessing complete!")
    print(f"  Output directory: {output_dir}")

    con.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python preprocess.py <input_csv> <output_dir>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    preprocess_mmrrc(input_file, output_dir)
