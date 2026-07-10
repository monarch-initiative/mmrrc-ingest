"""
Preprocessing script for MMRRC catalog data using DuckDB.

This script normalizes the denormalized MMRRC catalog CSV into separate files:
1. genotypes.csv - One row per unique genotype
2. genotype_to_phenotype.csv - One row per genotype-phenotype association
3. allele_to_genotype.csv - One row per allele-genotype association
4. genotype_to_gene.csv - One row per genotype-gene association

The MMRRC accession columns are dirty in places (tab-prefixed CURIEs like
``\\tMGI:5638932`` and wrong-namespace values like ``GeneID:23671``). We
normalize every identifier by extracting a canonical ``MGI:<digits>`` CURIE with
a regex; anything that does not contain a valid MGI CURIE is dropped rather than
emitted as a broken edge.
"""

from pathlib import Path

import duckdb


def preprocess_mmrrc(input_file: Path, output_dir: Path) -> None:
    """Preprocess MMRRC catalog data into normalized CSV files using DuckDB."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {input_file} into DuckDB...")
    con = duckdb.connect(":memory:")

    # Load the CSV file, treating all columns as VARCHAR to avoid type issues.
    con.execute(f"""
        CREATE TABLE mmrrc AS
        SELECT * FROM read_csv_auto('{input_file}', all_varchar=true)
    """)  # noqa: S608

    # Cleaned view: canonicalize the MGI accessions and PubMed IDs once so every
    # downstream extract inherits the same normalization. regexp_extract returns
    # '' when there is no match, which the WHERE clauses below filter out.
    con.execute(r"""
        CREATE VIEW clean AS
        SELECT
            "STRAIN/STOCK_ID"          AS strain_id,
            "STRAIN/STOCK_DESIGNATION" AS strain_designation,
            OTHER_NAMES                AS other_names,
            STRAIN_TYPE                AS strain_type,
            STATE                      AS state,
            regexp_extract(MGI_ALLELE_ACCESSION_ID, 'MGI:\d+') AS allele_id,
            ALLELE_SYMBOL              AS allele_symbol,
            ALLELE_NAME                AS allele_name,
            MUTATION_TYPE              AS mutation_type,
            CHROMOSOME                 AS chromosome,
            regexp_extract(MGI_GENE_ACCESSION_ID, 'MGI:\d+') AS gene_id,
            GENE_SYMBOL                AS gene_symbol,
            GENE_NAME                  AS gene_name,
            SDS_URL                    AS sds_url,
            ACCEPTED_DATE              AS accepted_date,
            MPT_IDS                    AS mpt_ids_raw,
            PUBMED_IDS                 AS pubmed_ids,
            RESEARCH_AREAS             AS research_areas
        FROM mmrrc
    """)

    result = con.execute("SELECT COUNT(*) FROM clean").fetchone()
    total_rows = result[0] if result else 0
    print(f"Loaded {total_rows} rows")

    # Strain-level publications: MMRRC lists PubMed IDs per strain (not per
    # allele/phenotype), formatted like "PMID: 123, PMID: 456". Normalize to
    # bare CURIEs and aggregate one pipe-delimited list per strain so edge
    # transforms can attach them as `publications`.
    con.execute(r"""
        CREATE TABLE strain_pubs AS
        SELECT strain_id, string_agg(DISTINCT pmid, '|' ORDER BY pmid) AS pubmed_ids
        FROM (
            SELECT strain_id, 'PMID:' || UNNEST(regexp_extract_all(pubmed_ids, '\d+')) AS pmid
            FROM clean
            WHERE pubmed_ids IS NOT NULL AND pubmed_ids != ''
        )
        GROUP BY strain_id
    """)

    # 1. genotypes.csv - one row per unique STRAIN/STOCK_ID
    print("\nCreating genotypes.csv...")
    genotypes_file = output_dir / "genotypes.csv"
    con.execute(f"""
        COPY (
            SELECT DISTINCT
                strain_id,
                FIRST(strain_designation) AS strain_designation,
                FIRST(other_names) AS other_names,
                FIRST(strain_type) AS strain_type,
                FIRST(state) AS state,
                FIRST(mutation_type) AS mutation_type,
                FIRST(chromosome) AS chromosome,
                FIRST(sds_url) AS sds_url,
                FIRST(accepted_date) AS accepted_date,
                FIRST(research_areas) AS research_areas,
                FIRST(pubmed_ids) AS pubmed_ids,
                FIRST(mpt_ids_raw) AS mpt_ids_raw
            FROM clean
            GROUP BY strain_id
            ORDER BY strain_id
        ) TO '{genotypes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608
    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{genotypes_file}')").fetchone()  # noqa: S608
    print(f"  Wrote {result[0] if result else 0} unique genotypes")

    # 2. allele_to_genotype.csv - one row per (allele, genotype) pair
    print("\nCreating allele_to_genotype.csv...")
    allele_genotypes_file = output_dir / "allele_to_genotype.csv"
    con.execute(f"""
        COPY (
            SELECT DISTINCT
                allele_id,
                allele_symbol,
                allele_name,
                strain_id,
                mutation_type,
                chromosome
            FROM clean
            WHERE allele_id != ''
            ORDER BY strain_id, allele_id
        ) TO '{allele_genotypes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608
    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{allele_genotypes_file}')").fetchone()  # noqa: S608
    print(f"  Wrote {result[0] if result else 0} allele-genotype associations")

    # 3. genotype_to_gene.csv - one row per (genotype, gene) pair, with the
    #    strain's publications attached. MMRRC identifies most strains by target
    #    gene rather than by an allele accession, so this connects the large
    #    gene-trap/targeted set that has no allele accession.
    print("\nCreating genotype_to_gene.csv...")
    genotype_genes_file = output_dir / "genotype_to_gene.csv"
    con.execute(f"""
        COPY (
            SELECT DISTINCT
                c.strain_id,
                c.gene_id,
                c.gene_symbol,
                c.gene_name,
                p.pubmed_ids
            FROM clean c
            LEFT JOIN strain_pubs p USING (strain_id)
            WHERE c.gene_id != ''
            ORDER BY c.strain_id, c.gene_id
        ) TO '{genotype_genes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608
    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{genotype_genes_file}')").fetchone()  # noqa: S608
    print(f"  Wrote {result[0] if result else 0} genotype-gene associations")

    # 4. genotype_to_phenotype.csv - explode MP IDs from MPT_IDS field
    print("\nCreating genotype_to_phenotype.csv...")
    genotype_phenotypes_file = output_dir / "genotype_to_phenotype.csv"
    con.execute(r"""
        CREATE TABLE phenotype_associations AS
        SELECT DISTINCT
            strain_id,
            UNNEST(regexp_extract_all(mpt_ids_raw, 'MP:\d+')) AS mp_id,
            mpt_ids_raw
        FROM clean
        WHERE mpt_ids_raw IS NOT NULL
          AND mpt_ids_raw != ''
          AND regexp_extract_all(mpt_ids_raw, 'MP:\d+') IS NOT NULL
    """)
    # Extract the human-readable label preceding each [MP:XXXXXXX] tag. The label
    # is best-effort only; the transform does not require it, so a failed
    # extraction never drops a real phenotype association.
    con.execute(f"""
        COPY (
            SELECT DISTINCT
                strain_id,
                mp_id AS phenotype_id,
                regexp_extract(
                    mpt_ids_raw,
                    '([^|\\[]+)\\s*\\[' || mp_id || '\\]',
                    1
                ) AS phenotype_label
            FROM phenotype_associations
            WHERE mp_id IS NOT NULL
            ORDER BY strain_id, mp_id
        ) TO '{genotype_phenotypes_file}' (HEADER, DELIMITER ',')
    """)  # noqa: S608
    result = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{genotype_phenotypes_file}')").fetchone()  # noqa: S608
    print(f"  Wrote {result[0] if result else 0} genotype-phenotype associations")

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
