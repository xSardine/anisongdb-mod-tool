def populate_url_with_args(url, args):
    is_first_arg = True
    for key, value in args.items():
        if value:
            if is_first_arg:
                url += f"?{key}={value}"
                is_first_arg = False
            else:
                url += f"&{key}={value}"
    return url


def get_query_args(request) -> dict:
    """
    Get query parameters from the URL using request.args and return them as a dict

    Parameters
    ----------
    request : request
        Request object from flask GET

    Returns
    ----------
    dict
        Dictionary containing the query parameters
    """

    query_args = {
        param: request.args.get(param, default_value)
        for param, default_value in request.args.items()
    }

    query_args["page"] = int(query_args["page"]) if "page" in query_args else 1
    query_args["page_size"] = (
        int(query_args["page_size"]) if "page_size" in query_args else 50
    )

    return query_args
