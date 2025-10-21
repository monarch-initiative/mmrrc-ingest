"""
Test file for MMRRC genotype transform.

Tests the transform of genotype nodes from preprocessed MMRRC data.
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Genotype
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from mmrrc_ingest.genotypes import transform_record


@pytest.fixture
def genotype_row() -> dict[str, str]:
    """Example genotype row from genotypes.csv"""
    return {
        "strain_id": "MMRRC:000001-UNC",
        "strain_designation": "C57BL/6-Tg(Fga,Fgb,Fgg)1Unc/Mmnc",
        "other_names": "RRID:MMRRC_000001-UNC",
        "strain_type": "MSR",
        "state": "CA",
        "mutation_type": "TG",
        "chromosome": "3",
        "sds_url": "https://www.mmrrc.org/catalog/sds.php?mmrrc_id=1",
        "accepted_date": "05/01/2001",
        "research_areas": "",
        "pubmed_ids": "PMID: 11521996",
        "mpt_ids_raw": "",
    }


@pytest.fixture
def genotype_entity(genotype_row: dict[str, str]) -> Genotype:
    """Transform a genotype row"""
    koza_transform = KozaTransform(mappings={}, writer=PassthroughWriter(), extra_fields={})
    result = transform_record(koza_transform, genotype_row)
    return result[0] if result else None


def test_genotype_id(genotype_entity: Genotype) -> None:
    """Test genotype ID is correctly assigned"""
    assert genotype_entity.id == "MMRRC:000001-UNC"


def test_genotype_name(genotype_entity: Genotype) -> None:
    """Test genotype name is the strain designation"""
    assert genotype_entity.name == "C57BL/6-Tg(Fga,Fgb,Fgg)1Unc/Mmnc"


def test_genotype_xref(genotype_entity: Genotype) -> None:
    """Test genotype xref includes RRID"""
    assert "RRID:MMRRC_000001-UNC" in genotype_entity.xref


def test_genotype_taxon(genotype_entity: Genotype) -> None:
    """Test genotype taxon is Mus musculus"""
    assert genotype_entity.in_taxon == ["NCBITaxon:10090"]
    assert genotype_entity.in_taxon_label == "Mus musculus"


def test_genotype_provided_by(genotype_entity: Genotype) -> None:
    """Test genotype provenance"""
    assert genotype_entity.provided_by == ["infores:mmrrc"]


def test_genotype_category(genotype_entity: Genotype) -> None:
    """Test genotype has correct biolink category"""
    assert "biolink:Genotype" in genotype_entity.category
