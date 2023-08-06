from datetime import datetime as dt


# prints a user friendly error message if the dob is not formatted properly
def check_dob_format(dob):
    try:
        if dob is not None:
            dt.strptime(dob, "%Y-%m-%d")
    except ValueError as error:
        error.args = (
            "The date `{0}` does not match the format YYYY-MM-DD".format(dob),
        )
        raise


def filter_del_lines_from_load_annotations(call):
    return call.get("alt", "") != "<DEL>"


def filter_bnd_cpx_ctx_lns_from_load_annotations(call):
    """If the dict[alt] is not equal to any of the unwanteds then return true
    so that the filter option will gather all of the lines that were
    considered true and dispose the lines that are false. Essentially we
    are leveraging the filter() funciton to remove any lines with
     alt==unwanted"""

    unwanteds = ("<BND>", "<CPX>", "<CTX>")
    return call.get("alt", "") not in unwanteds
