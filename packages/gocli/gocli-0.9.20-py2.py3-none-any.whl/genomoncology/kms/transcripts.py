from cytoolz.curried import curry

from gosdk import logger


@curry
def process_transcript_batch(data, sdk=None):
    record = {
        "batch": [
            "%s|%s|%s" % (record["chromosome"], record["start"], record["end"])
            for record in data
        ]
    }
    logger.get_logger().debug("get_transcripts_batch", **record)

    results = sdk.call_with_retry(
        sdk.region_search.region_search_batch, **record
    )["results"]
    return results


@curry
def process_transcript_batch_get_genes(data, sdk=None):
    record = {
        "batch": [
            "%s|%s|%s" % (record["chromosome"], record["start"], record["end"])
            for record in data
        ]
    }
    logger.get_logger().debug("get_transcripts_batch", **record)
    # Get all regions for the genes
    results = sdk.call_with_retry(
        sdk.region_search.region_search_batch, **record
    )["results"]
    # we only need the gene names from the result that is returned,
    # We also do not want duplicate names.
    list_of_genes = []
    for line in results:
        transcripts = line.get("transcripts", [])
        for transcript in transcripts:
            list_of_genes.append(transcript.get("gene"))
    return set(list_of_genes)
