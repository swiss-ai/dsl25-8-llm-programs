def split_parser(response, separator):
    """
    Parse the response into a list, splitting by the given separator
    """
    return [line.strip() for line in response.split(separator) if line.strip()]


def lines_parser(response):
    """
    Parse the response into a list of lines
    """
    return split_parser(response, "\n")