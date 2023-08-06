import re
from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "chr": "chr",
    "gene": "gene_name",
    "alterations": "alterations",
    "CNT__int": "CNT",
    "tissues__mstring": "TISSUES",
    "tissue_cnt__mstring": "TISSUES",
    "tissue_frequency__mstring": "TISSUES_FREQ",
    "tissue_subtype_cnt__mstring": "TISSUES_SUBTYPE",
    "tissue_subtype_frequency__mstring": "TISSUES_SUBTYPE_FREQ",
    "histology_cnt__mstring": "HISTOLOGY",
    "histology_frequency__mstring": "HISTOLOGY_FREQ",
    "histology_subtype_cnt__mstring": "HISTOLOGY_SUBTYPE",
    "histology_subtype_frequency__mstring": "HISTOLOGY_SUBTYPE_FREQ"
}

def get_keys(x, field):
    return list(x.get(field, {}).keys())


def process_frequency_and_counts(x, field):
    freq_results = []
    freq_info = x.get(field)
    for tissue, freq in freq_info.items():
        freq_results.append(f"{tissue}={freq}")
    return freq_results


def remove_start_field(x):
    x.pop("start", "")
    return x


def get_chr(x):
    if x.get("chr"):
        result = re.search(r"(\d{1,2}\b)", x.get("chr", ""))
        return int(result.group())



register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.COSMIC_NON_SNV,
    transformer=compose(
        lambda x: assoc(
            x, "tissues__mstring", get_keys(x, "tissues__mstring")
        ),
        lambda x: assoc(
            x,
            "tissue_cnt__mstring",
            process_frequency_and_counts(x, "tissue_cnt__mstring"),
        ),
        lambda x: assoc(
            x,
            "tissue_frequency__mstring",
            process_frequency_and_counts(x, "tissue_frequency__mstring"),
        ),
        lambda x: assoc(
            x,
            "tissue_subtype_cnt__mstring",
            process_frequency_and_counts(x, "tissue_subtype_cnt__mstring"),
        ),
        lambda x: assoc(
            x,
            "tissue_subtype_frequency__mstring",
            process_frequency_and_counts(
                x, "tissue_subtype_frequency__mstring"
            ),
        ),
        lambda x: assoc(
            x,
            "histology_cnt__mstring",
            process_frequency_and_counts(x, "histology_cnt__mstring"),
        ),
        lambda x: assoc(
            x,
            "histology_frequency__mstring",
            process_frequency_and_counts(x, "histology_frequency__mstring"),
        ),
        lambda x: assoc(
            x,
            "histology_subtype_cnt__mstring",
            process_frequency_and_counts(x, "histology_subtype_cnt__mstring"),
        ),
        lambda x: assoc(
            x,
            "histology_subtype_frequency__mstring",
            process_frequency_and_counts(
                x, "histology_subtype_frequency__mstring"
            ),
        ),
        lambda x: assoc(x, "chr", get_chr(x)),
        lambda x: assoc(x, __TYPE__, DocType.COSMIC_NON_SNV.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.COSMIC_NON_SNV,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.COSMIC_NON_SNV.value)),
    is_header=True,
)
