from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "chr": "chr",
    "start": "start",
    "build": "build",
    "pos": "start",
    "fusion_partner_chr": "chr",
    "fusion_partner_position": "end",
    "fallback_fp_position": "info.SVEND",
    "copy_number": "info.CN",
    "alt": "alt",
    "insertion_length": "info.SVINSLEN",
    "insertion_sequence": "info.SVINSSEQ",
    "mutation_type": "info.SVTYPE",
    "fallback_mutation_type": "info.TYPEOFSV",
    "mate_id": "info.MATEID",
    "id": "id",
}


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
            f"{prefix_generator}{str(dict.get(key))}"
            if dict.get(key) is not None and key in dict
            else ""
        )  # noqa: E501
    elif hasattr(dict.get(key), "__iter__"):
        return (
            f"|{prefix_generator}{dict.get(key)[0]}"
            if dict.get(key) is not None and key in dict
            else ""
        )  # noqa: E501
    else:
        return (
            f"|{prefix_generator}{dict.get(key)}"
            if dict.get(key) is not None and key in dict
            else ""
        )  # noqa: E501


def get_chr_info(x):
    new_string = f'{get_val_or_empty_string(x,"chr")}:' f'{get_val_or_empty_string(x,"start")}'
    return new_string


def get_extra_info(x):
    # This constructs everything past the portion of the chr/fusion section
    # of an sv hash
    new_string = f'{get_val_or_empty_string(x,"mutation_type")}' f'{get_val_or_empty_string(x,"insertion_length")}' f'{get_val_or_empty_string(x,"insertion_sequence")}' f'{get_val_or_empty_string(x,"copy_number")}'
    return new_string


def get_mutation_type(x):
    if x.get("mutation_type", None):
        return x["mutation_type"]
    elif x.get("fallback_mutation_type", None):
        return x.pop("fallback_mutation_type")
    else:
        return ""


def get_fusion_partner_position(x):
    # fusion_partner_position will always be defined. If missing it == start/pos
    if int(x["fusion_partner_position"]) == x["start"] and x.get(
        "fallback_fp_position", None
    ):
        return int(x.pop("fallback_fp_position"))
    else:
        return x["fusion_partner_position"]


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

    # This line goes here because lambdas in compose() are evaluated left to right
    new_string = f'{get_val_or_empty_string(x, "chr")}:' f'{get_val_or_empty_string(x, "start")}|' f'{get_val_or_empty_string(x, "fusion_partner_chr")}:' f'{get_val_or_empty_string(x, "fusion_partner_position")}|' f'{get_val_or_empty_string(x, "mutation_type")}' f'{get_val_or_empty_string(x, "insertion_length")}' f'{get_val_or_empty_string(x, "insertion_sequence")}' f'{get_val_or_empty_string(x, "copy_number")}'
    # once the string is created properly, we return the string which will be
    # the value for the key of "sv_hash"
    return new_string


register(
    input_type=DocType.CALL,
    output_type=DocType.SV_HASH,
    transformer=compose(
        lambda x: assoc(x, "sv_hash", sv_hash_generator(x)),
        lambda x: assoc(x, "mutation_type", get_mutation_type(x)),
        lambda x: assoc(
            x, "fusion_partner_position", get_fusion_partner_position(x)
        ),
        lambda x: assoc(x, "chr_info", get_chr_info(x)),
        lambda x: assoc(x, "extra_info", get_extra_info(x)),
        lambda x: assoc(x, __TYPE__, DocType.SV_HASH.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.SV_HASH,
    transformer=compose(
        lambda x: assoc(x, __CHILD__, DocType.SV_HASH.value)
    ),  # noqa: E501
    is_header=True,
)
