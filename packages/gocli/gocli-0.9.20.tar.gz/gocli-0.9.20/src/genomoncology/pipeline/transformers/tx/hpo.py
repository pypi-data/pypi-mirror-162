from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "gene": "gene",
    # info
    "NCBI_id": "gene_id",
    "phenotype__mstring": "phenotype",
    "hpo__mstring": "hpo_id",
}


def parse_hpo_gene(x):
    return x["key"]


def dedupe_gene_id(x):
    gene_ids = x.get("gene_id", None)
    if gene_ids:
        return list(set(gene_ids))


register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.HPO,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.HPO.value),
        name_mapping(NAME_MAPPING),
        lambda x: assoc(x, "gene_id", dedupe_gene_id(x)),
        lambda x: assoc(x, "gene", parse_hpo_gene(x)),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.HPO,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.HPO.value),
    ),
    is_header=True,
)
