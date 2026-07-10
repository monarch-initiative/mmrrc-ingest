# MMRRC (Mutant Mouse Resource & Research Centers)

The MMRRC is a national resource that archives and distributes genetically engineered mouse strains to the research community. This ingest captures genotype nodes and allele-to-genotype, genotype-to-gene, and genotype-to-phenotype associations from the MMRRC catalog data.

* [MMRRC Website](https://www.mmrrc.org)
* [MMRRC Data Catalog](https://www.mmrrc.org/about/mmrrc_catalog_data.csv)
* [MMRRC API Documentation](http://api.mmrrc.org/files/MMRRC_API.pdf)

## Data Source

**Download**: https://www.mmrrc.org/about/mmrrc_catalog_data.csv

The catalog is provided as a single denormalized CSV where each row represents a strain, but with one-to-many relationships embedded: a genotype (identified by STRAIN/STOCK_ID) can have multiple alleles and multiple associated genes, and phenotypes are stored as pipe-delimited lists of Mammalian Phenotype Ontology terms (e.g. `phenotype label [MP:XXXXXXX]`).

### Preprocessing

The denormalized catalog is normalized into four datasets before transformation:

1. **Genotypes** — Deduplicated by strain ID to produce one row per unique genotype
2. **Allele-to-genotype** — Distinct pairs of MGI allele accession IDs and strain IDs, filtering out rows with no allele accession
3. **Genotype-to-gene** — Distinct pairs of strain IDs and MGI gene accession IDs, with the strain's PubMed IDs attached. MMRRC identifies most strains by target gene rather than allele accession, so this covers the large gene-trap/targeted set that carries no allele
4. **Genotype-to-phenotype** — The pipe-delimited phenotype lists are exploded into individual MP term associations per genotype, with phenotype labels extracted from the structured text

Duplicate relationships in the original catalog (e.g. the same genotype-allele pair appearing multiple times) are deduplicated during this step.

**Identifier normalization**: MMRRC accession columns contain dirty values (tab-prefixed CURIEs like `\tMGI:5638932`, wrong-namespace values like `GeneID:23671`). Every allele and gene identifier is normalized by extracting a canonical `MGI:<digits>` CURIE; values with no valid MGI CURIE are dropped rather than emitted as broken edges. PubMed IDs (`PMID: 123`) are normalized to bare `PMID:123` CURIEs.

## Genotype

Creates Genotype nodes for each unique mouse strain in the MMRRC catalog. All MMRRC strains are _Mus musculus_, so taxon is hardcoded.

**Biolink Captured:**

* **biolink:Genotype**
    * id: `MMRRC:{strain_id}` (already in format `MMRRC:XXXXXX-XXX`)
    * name: `strain_designation` - Full strain designation with genetic nomenclature
    * xref: `other_names` - Includes RRID identifiers
    * in_taxon: `["NCBITaxon:10090"]` (Mus musculus - hardcoded)
    * in_taxon_label: `"Mus musculus"`
    * provided_by: `["infores:mmrrc"]`

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

## Genotype to Phenotype

Associations between genotypes and their observed phenotypes using Mammalian Phenotype Ontology (MP) terms. Rows with empty phenotype IDs or labels are filtered out.

**Biolink Captured:**

* **biolink:GenotypeToPhenotypicFeatureAssociation**
    * id: Generated UUID
    * subject: `strain_id` (Genotype ID, e.g., `MMRRC:000002-UNC`)
    * predicate: `biolink:has_phenotype`
    * object: `phenotype_id` (e.g., `MP:0000063`)
    * aggregator_knowledge_source: `["infores:monarchinitiative"]`
    * primary_knowledge_source: `"infores:mmrrc"`
    * knowledge_level: `"knowledge_assertion"`
    * agent_type: `"manual_agent"`

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

## Allele to Genotype

Associations between MGI alleles and the MMRRC genotypes that carry them.

**Biolink Captured:**

* **biolink:GenotypeToVariantAssociation** (using Allele as a type of Variant)
    * id: Generated UUID
    * subject: `strain_id` (Genotype ID, e.g., `MMRRC:000002-UNC`)
    * predicate: `biolink:has_sequence_variant` (inverse: genotype has_sequence_variant allele)
    * object: `allele_id` (MGI Allele ID, e.g., `MGI:2152217`)
    * aggregator_knowledge_source: `["infores:monarchinitiative"]`
    * primary_knowledge_source: `"infores:mmrrc"`
    * knowledge_level: `"knowledge_assertion"`
    * agent_type: `"manual_agent"`

### Design Decision

We use `GenotypeToVariantAssociation` with `has_sequence_variant` predicate rather than creating a separate `AlleleToGenotypeAssociation` type, as Biolink Model treats alleles as a type of sequence variant. The direction is: Genotype (subject) -> has_sequence_variant -> Allele (object), which allows us to express that this allele is part of/contributes to this genotype.

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

## Genotype to Gene

Associations between MMRRC genotypes and the MGI genes they target. MMRRC records a target gene (`MGI_GENE_ACCESSION_ID`) for most strains — including the large gene-trap/targeted set that has no allele accession — so this transform is the primary way these strains connect to genes.

**Biolink Captured:**

* **biolink:GenotypeToGeneAssociation**
    * id: Generated UUID
    * subject: `strain_id` (Genotype ID, e.g., `MMRRC:000002-UNC`)
    * predicate: `biolink:related_to` (deliberately vague, matching the Alliance genotype→gene convention)
    * object: `gene_id` (MGI Gene ID, e.g., `MGI:109392`)
    * publications: the strain's `PUBMED_IDS`, normalized to `PMID:` CURIEs
    * aggregator_knowledge_source: `["infores:monarchinitiative"]`
    * primary_knowledge_source: `"infores:mmrrc"`
    * knowledge_level: `"knowledge_assertion"`
    * agent_type: `"manual_agent"`

### Design Decision

We use `GenotypeToGeneAssociation` with `biolink:related_to`, following the Alliance ingest convention (`kozahub/alliance-ingest`), which keeps the predicate intentionally vague because the strain→gene relationship in these catalogs is not a specific molecular one. MMRRC's PubMed IDs are recorded at the strain level (not per allele or phenotype), so they are attached as `publications` here as the strain's defining references.

#### Example Input

```csv
strain_id,gene_id,gene_symbol,gene_name,pubmed_ids
MMRRC:000002-UNC,MGI:109392,Esr2,estrogen receptor 2 (beta),PMID:9861029
```

#### Example Output

```python
GenotypeToGeneAssociation(
    id="uuid:...",
    subject="MMRRC:000002-UNC",
    predicate="biolink:related_to",
    object="MGI:109392",
    publications=["PMID:9861029"],
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:mmrrc",
    knowledge_level="knowledge_assertion",
    agent_type="manual_agent"
)
```

## Not Ingested: Genotype model_of Disease

The per-strain `getSDS` API exposes DOID annotations under `alterations[].doid_ids`, which is tempting as a source of `model_of` disease edges. On inspection these are **Disease Ontology gene→disease associations for the strain's target gene(s)**, not curated strain-as-model annotations: multi-gene deletion strains accumulate the union of every deleted gene's disease associations (one strain reached 241 diseases across ~230 genes), and 87% of the ~548k candidate edges come from such multi-gene strains. This is redundant with the `genotype→gene` edges above plus Monarch's existing gene→disease sources (strain→gene→disease is reachable by traversal), and `model_of` would misrepresent the relationship, so these are deliberately not ingested.

## Citation

Mutant Mouse Resource & Research Centers (MMRRC). https://www.mmrrc.org
