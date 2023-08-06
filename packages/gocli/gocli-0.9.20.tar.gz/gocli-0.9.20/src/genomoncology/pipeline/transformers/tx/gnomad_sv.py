from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "chr": "chr",
    "start": "start",
    "build": "build",
    "pos": "start",
    "fusion_partner_chr": "chr",
    "copy_number": "alt",
    "insertion_length": "info.SVLEN",
    "mutation_type": "info.SVTYPE",
    "AN__int": "info.AN",
    "AC__int": "info.AC",
    "AF__float": "info.AF",
    "N_BI_GENOS__int": "info.N_BI_GENOS",
    "N_HOMREF__int": "info.N_HOMREF",
    "N_HET__int": "info.N_HET",
    "N_HOMALT__int": "info.N_HOMALT",
    "FREQ_HOMREF__float": "info.FREQ_HOMREF",
    "FREQ_HET__float": "info.FREQ_HET",
    "FREQ_HOMALT__float": "info.FREQ_HOMALT",
    "MALE_AN__int": "info.MALE_AN",
    "MALE_AC__int": "info.MALE_AC",
    "MALE_AF__float": "info.MALE_AF",
    "MALE_N_BI_GENOS__int": "info.MALE_N_BI_GENOS",
    "MALE_N_HOMREF__int": "info.MALE_N_HOMREF",
    "MALE_N_HET__int": "info.MALE_N_HET",
    "MALE_N_HOMALT__int": "info.MALE_N_HOMALT",
    "MALE_FREQ_HOMREF__float": "info.MALE_FREQ_HOMREF",
    "MALE_FREQ_HET__float": "info.MALE_FREQ_HET",
    "MALE_FREQ_HOMALT__float": "info.MALE_FREQ_HOMALT",
    "FEMALE_AN__int": "info.FEMALE_AN",
    "FEMALE_AC__int": "info.FEMALE_AC",
    "FEMALE_AF__float": "info.FEMALE_AF",
    "FEMALE_N_BI_GENOS__int": "info.FEMALE_N_BI_GENOS",
    "FEMALE_N_HOMREF__int": "info.FEMALE_N_HOMREF",
    "FEMALE_N_HET__int": "info.FEMALE_N_HET",
    "FEMALE_N_HOMALT__int": "info.FEMALE_N_HOMALT",
    "FEMALE_FREQ_HOMREF__float": "info.FEMALE_FREQ_HOMREF",
    "FEMALE_FREQ_HET__float": "info.FEMALE_FREQ_HET",
    "FEMALE_FREQ_HOMALT__float": "info.FEMALE_FREQ_HOMALT",
    "AFR_AN__int": "info.AFR_AN",
    "AFR_AC__int": "info.AFR_AC",
    "AFR_AF__float": "info.AFR_AF",
    "AMR_AN__int": "info.AMR_AN",
    "AMR_AC__int": "info.AMR_AC",
    "AMR_AF__float": "info.AMR_AF",
    "EAS_AN__int": "info.EAS_AN",
    "EAS_AC__int": "info.EAS_AC",
    "EAS_AF__float": "info.EAS_AF",
    "EUR_AN__int": "info.EUR_AN",
    "EUR_AC__int": "info.EUR_AC",
    "EUR_AF__float": "info.EUR_AF",
    "OTH_AN__int": "info.OTH_AN",
    "OTH_AC__int": "info.OTH_AC",
    "OTH_AF__float": "info.OTH_AF",
    "POPMAX_AF__float": "info.POPMAX_AF",
    "end": "end",
    "end2": "info.END2",
}


def copy_number_generator(x):
    """This function takes argument 'x' which is the dictionary that is created
     using the below lambda functions. The function iterates over the current
      copy_number value in order to edit the value to store a number or null"""
    temp_str = x.get("copy_number", None)
    # check if string has ints. If so then return ints only,
    # or return original value
    check_for_ints = "".join(list(i for i in temp_str if i.isdigit()))
    if len(check_for_ints) > 0:
        return int(check_for_ints)
    else:
        return None


def fusion_partner_parser(x):
    """this function takes argument 'x' which is the dictionary that is
    created using the below lambda functions. The functions returns the
     appropriate value so that it can be associated with the
     fusion_partner_position key in the lambda function below."""
    end_options = ("DEL", "DUP", "INV", "CNV")
    if x.get("mutation_type", None) in end_options:
        return x["end"]
    if x.get("mutation_type", None) == "INS":
        return x["end2"]


def get_val_or_empty_string(dict, key):

    """ this function returns the value or an empty string of a key in the
     given dictionary. Since some values are None we can not use the default
      value returned for .get() method since we need an empty string rather
    than None"""

    """ We are building a string that looks like this ->
    c:position|fusion_partner_c:fusion_partner_position
    |INS_LEN=insertion_length|INS_SEQ=insertion_sequence|
    REL_ORIEN:relative_orientation|CN=copy_number
    *** there is various logic that must be implemented
    in terms of which fields to output and how
    the output should look based on conditions."""

    # dict that maps the previous names to the new names for the sv_hash field
    output_keys = {
        "copy_number": "CN",
        "insertion_length": "INS_LEN",
        "insertion_sequence": "INS_SEQ",
        "relative_orientation": "REL_ORIEN",
    }  # noqa: E501

    mandatory_fields = (
        "chr",
        "start",
        "fusion_partner_chr",
        "fusion_partner_position",
        "mutation_type",
    )  # noqa: E501
    prefix_generator = (
        f"{output_keys[key]}=" if key not in mandatory_fields else ""
    )  # noqa: E501
    if key in mandatory_fields:
        return (
            f"{prefix_generator}{dict.get(key)}"
            if dict.get(key) is not None and key in dict
            else ""
        )  # noqa: E501

    elif key == "insertion_length" and dict.get("mutation_type") == "INS":
        return (
            f"|{prefix_generator}{dict.get(key)}"
            if dict.get(key) is not None and key in dict
            else ""
        )  # noqa: E501

    else:

        return (
            f"|{prefix_generator}{dict.get(key)}"
            if dict.get(key) is not None and key in dict
            else ""
        )  # noqa: E501


def sv_hash_generator(x):
    """this function takes argument 'x' which is the dictionary that is
    created  using the below lambda functions.
    The function returns a f' string that is formatted using the
     existing fields  in the dictionary in order to create
     the following string  where the value is not null or None
    this is the string ->
    c: position | fusion_partner_chr:fusion_partner_position |
    insertion_length
     | insertion_sequence | relative_orientation | copy_number
    mutation_type For example, this should be returned in an
    instance where some
     fields are present while others missing:
    "sv_hash":"1:54665|1:54716|52||||"""
    # creates a new dict with only values that are not Null and separated using
    # the delimiter as requested in the ticket.
    new_string = f'{get_val_or_empty_string(x,"chr")}:' f'{get_val_or_empty_string(x,"start")}|' f'{get_val_or_empty_string(x,"fusion_partner_chr")}:' f'{get_val_or_empty_string(x,"fusion_partner_position")}|' f'{get_val_or_empty_string(x,"mutation_type")}' f'{get_val_or_empty_string(x,"insertion_length")}' f'{get_val_or_empty_string(x,"insertion_sequence")}' f'{get_val_or_empty_string(x,"relative_orientation")}' f'{get_val_or_empty_string(x,"copy_number")}'
    # once the string is created properly, we return the string which will be
    # the value for the key of "sv_hash"
    return new_string


register(
    input_type=DocType.CALL,
    output_type=DocType.GNOMAD_SV,
    transformer=compose(
        lambda x: assoc(x, "sv_hash", sv_hash_generator(x)),
        lambda x: assoc(x, "copy_number", copy_number_generator(x)),
        lambda x: assoc(
            x, "fusion_partner_position", fusion_partner_parser(x)
        ),  # noqa: E501,E261,E262
        lambda x: assoc(
            x,
            "mutation_type",
            "CNV"
            if x.get("mutation_type", None) == "MCNV"
            else x.get("mutation_type"),
        ),  # noqa: E501,E261,E262
        lambda x: assoc(
            x,
            "insertion_length",
            None
            if x.get("mutation_type", None) != "INS"
            else x.get("insertion_length"),
        ),  # noqa: E501
        lambda x: assoc(x, __TYPE__, DocType.GNOMAD_SV.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.GNOMAD_SV,
    transformer=compose(
        lambda x: assoc(x, __CHILD__, DocType.GNOMAD_SV.value)
    ),  # noqa: E501
    is_header=True,
)
