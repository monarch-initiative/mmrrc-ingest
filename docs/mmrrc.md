# MMRRC (Mutant Mouse Resource & Research Centers)

The MMRRC is a national resource that archives and distributes genetically engineered mouse strains to the research community. This ingest captures genotype information, allele-to-genotype associations, and genotype-to-phenotype associations from the MMRRC catalog data.

* [MMRRC Website](https://www.mmrrc.org)
* [MMRRC Data Catalog](https://www.mmrrc.org/about/mmrrc_catalog_data.csv)
* [MMRRC API Documentation](http://api.mmrrc.org/files/MMRRC_API.pdf)

## Data Source

**Download**: https://www.mmrrc.org/about/mmrrc_catalog_data.csv

The catalog CSV file contains 588,205 rows representing denormalized data about mouse strains. The data structure has one-to-many relationships:
- One genotype (STRAIN/STOCK_ID) can have multiple alleles
- One genotype can have multiple associated genes
- Phenotypes (MPT_IDS) are stored as pipe-delimited lists with format: `phenotype label [MP:XXXXXXX]`

## Preprocessing

The raw MMRRC catalog data is preprocessed using DuckDB (see `src/mmrrc-ingest/preprocess.py`) to normalize the denormalized structure into three separate CSV files:

1. **genotypes.csv** (69,025 rows) - One row per unique genotype
2. **allele_to_genotype.csv** (43,870 rows) - Allele-to-genotype associations
3. **genotype_to_phenotype.csv** (46,006 rows) - Genotype-to-phenotype associations with exploded MP IDs

### Preprocessing Logic

**Genotypes**: Deduplicated by `STRAIN/STOCK_ID`, keeping the first occurrence of descriptive fields.

**Allele-to-Genotype**: Filters rows where `MGI_ALLELE_ACCESSION_ID` is not null, creating distinct allele-genotype pairs.

**Genotype-to-Phenotype**:
- Extracts all MP IDs from the `MPT_IDS` field using regex: `MP:\\d+`
- Unnests/explodes the pipe-delimited phenotype list into individual associations
- Extracts phenotype labels by parsing text before each `[MP:XXXXXXX]` bracket

## Transforms

### 1. Genotype Nodes

**Source**: `data/processed/genotypes.csv`

**Transform**: `genotypes`

Creates Genotype nodes for each unique mouse strain in the MMRRC catalog.

#### Biolink Mapping

* **biolink:Genotype**
    * id: `MMRRC:{strain_id}` (already in format `MMRRC:XXXXXX-XXX`)
    * name: `strain_designation` - Full strain designation with genetic nomenclature
    * description: Constructed from `strain_type` and genetic information
    * xref: `other_names` - Includes RRID identifiers
    * in_taxon: `["NCBITaxon:10090"]` (Mus musculus - hardcoded)
    * in_taxon_label: `"Mus musculus"`
    * provided_by: `["infores:mmrrc"]`

#### Filtering/Branching Logic

- **No filtering**: All genotypes are included
- **Taxon assignment**: All MMRRC strains are mouse (Mus musculus), so taxon is hardcoded

#### Example Input

```csv
strain_id,strain_designation,other_names,strain_type,state,mutation_type,chromosome,sds_url,accepted_date,research_areas,pubmed_ids
MMRRC:000002-UNC,B6.129P2-<i>Esr2<sup>tm1Unc</sup></i>/Mmnc,RRID:MMRRC_000002-UNC,CON,CA,TM,12,https://www.mmrrc.org/catalog/sds.php?mmrrc_id=2,04/24/2001,,PMID: 9861029
```

#### Example Output

```python
Genotype(
    id="MMRRC:000002-UNC",
    name="B6.129P2-<i>Esr2<sup>tm1Unc</sup></i>/Mmnc",
    xref=["RRID:MMRRC_000002-UNC"],
    in_taxon=["NCBITaxon:10090"],
    in_taxon_label="Mus musculus",
    provided_by=["infores:mmrrc"]
)
```

### 2. Genotype-to-Phenotype Associations

**Source**: `data/processed/genotype_to_phenotype.csv`

**Transform**: `genotype_to_phenotype`

Creates associations between genotypes and their observed phenotypes using Mammalian Phenotype Ontology (MP) terms.

#### Biolink Mapping

* **biolink:GenotypeToPhenotypicFeatureAssociation**
    * id: Generated UUID using `koza_app.get_edge_id()`
    * subject: `strain_id` (Genotype ID, e.g., `MMRRC:000002-UNC`)
    * predicate: `biolink:has_phenotype`
    * object: `phenotype_id` (e.g., `MP:0000063`)
    * aggregator_knowledge_source: `["infores:monarchinitiative"]`
    * primary_knowledge_source: `"infores:mmrrc"`
    * knowledge_level: `"knowledge_assertion"`
    * agent_type: `"manual_agent"`

#### Filtering/Branching Logic

- **Filter empty phenotype IDs**: Skip rows where `phenotype_id` is null or empty
- **Filter empty phenotype labels**: Skip rows where label extraction failed (empty string)
- **No branching**: All associations follow the same pattern

#### Example Input

```csv
strain_id,phenotype_id,phenotype_label
MMRRC:000002-UNC,MP:0000063,decreased bone mineral density
MMRRC:000002-UNC,MP:0000137,abnormal vertebrae morphology
```

#### Example Output

```python
GenotypeToPhenotypicFeatureAssociation(
    id="uuid:...",
    subject="MMRRC:000002-UNC",
    predicate="biolink:has_phenotype",
    object="MP:0000063",
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:mmrrc",
    knowledge_level="knowledge_assertion",
    agent_type="manual_agent"
)
```

### 3. Allele-to-Genotype Associations

**Source**: `data/processed/allele_to_genotype.csv`

**Transform**: `allele_to_genotype`

Creates associations between MGI alleles and the MMRRC genotypes that carry them.

#### Biolink Mapping

* **biolink:GenotypeToVariantAssociation** (using Allele as a type of Variant)
    * id: Generated UUID using `koza_app.get_edge_id()`
    * subject: `strain_id` (Genotype ID, e.g., `MGI:2152217`)
    * predicate: `biolink:has_sequence_variant` (inverse: genotype has_sequence_variant allele)
    * object: `allele_id` (MGI Allele ID, e.g., `MMRRC:000002-UNC`)
    * aggregator_knowledge_source: `["infores:monarchinitiative"]`
    * primary_knowledge_source: `"infores:mmrrc"`
    * knowledge_level: `"knowledge_assertion"`
    * agent_type: `"manual_agent"`

#### Filtering/Branching Logic

- **Filter null alleles**: Skip rows where `allele_id` is null or empty
- **Filter null genotypes**: Skip rows where `strain_id` is null or empty
- **No branching**: All associations follow the same pattern

#### Design Decision

We use `GenotypeToVariantAssociation` with `has_sequence_variant` predicate rather than creating a separate `AlleleToGenotypeAssociation` type, as Biolink Model treats alleles as a type of sequence variant. The direction is: Genotype (subject) → has_sequence_variant → Allele (object), which allows us to express that this allele is part of/contributes to this genotype.

Alternative considered: Using `biolink:part_of` or `biolink:has_part`, but `has_sequence_variant` better captures the genetic relationship in Biolink's model.

#### Example Input

```csv
allele_id,allele_symbol,allele_name,strain_id,mutation_type,chromosome
MGI:2152217,Esr2<tm1Unc>,"estrogen receptor 2 (beta); targeted mutation 1, University of North Carolina",MMRRC:000002-UNC,TM,12
```

#### Example Output

```python
GenotypeToVariantAssociation(
    id="uuid:...",
    subject="MMRRC:000002-UNC",
    predicate="biolink:has_sequence_variant",
    object="MGI:2152217",
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:mmrrc",
    knowledge_level="knowledge_assertion",
    agent_type="manual_agent"
)
```

## Data Quality Notes

1. **Date Format Issues**: The `ACCEPTED_DATE` field contains invalid dates like `00/00/0000`, so all CSV columns are treated as VARCHAR during preprocessing
2. **HTML in Strain Names**: Strain designations contain HTML formatting (`<i>`, `<sup>`) which is preserved in the name field
3. **Missing Phenotype Labels**: Some phenotypes may have MP IDs but no associated labels due to regex extraction limitations
4. **Duplicate Rows**: The original catalog has duplicate relationships (e.g., same genotype-allele pair multiple times), which are deduplicated during preprocessing using `DISTINCT`

## Citation

Mutant Mouse Resource & Research Centers (MMRRC). https://www.mmrrc.org
