from fuzzywuzzy import fuzz


def ratio(t1, t2, ratio_type="default"):
    """

    :param t1: Text string 1
    :param t2: Text String 2
    :param ratio_type: Type of ratio score to be calculated between the two strings, default set to Ratio.
    :return: The Ratio of similarity among the texts with 100 being a complete match and 0 being no match.
    """
    switcher = {
        "Ratio": ratio,
        "partialRatio": partialRatio,
        "tokenSetRatio": tokenSetRatio,
        "tokenSortRatio": tokenSortRatio,
        "partialTokenSortRatio": partialTokenSortRatio,
        "qRatio": qRatio,
        "wRatio": wRatio,
    }
    if ratio_type not in ("Ratio", "qRatio", "wRatio", "partialRatio", "tokenSetRatio", "tokenSortRatio", "partialTokenSortRatio"):
        result = fuzz.ratio(t1, t2)
    else:
        result = switcher[ratio_type](t1, t2)
        # Call the appropriate function as per ratio type passed in the function call
    return result


def partialRatio(t1, t2):
    """
        :param t1: Text string 1
        :param t2: Text String 2
        :return: Returns the Partial Ratio score etween the two given text

        Function to calculate the ratio of the most similar substring as a number between 0 and 100.

        Example : "" and "" returns a score of :
    """
    return fuzz.partial_ratio(t1, t2)


def tokenSetRatio(t1, t2):
    """
        :param t1: Text string 1
        :param t2: Text String 2
        :return: Returns the Token Set Ratio score between the two given text

        Function to calculate the ratio of??????????????????????????

        Example : "" and "" returns a score of :
    """
    return fuzz.token_set_ratio(t1, t2)


def tokenSortRatio(t1, t2):
    """
        :param t1: Text string 1
        :param t2: Text String 2
        :return: Returns the Token Sort Ratio score between the two given text

        Function to calculate the ratio of??????????????????????????

        Example : "" and "" returns a score of :
    """
    return fuzz.token_sort_ratio(t1, t2)


def partialTokenSortRatio(t1, t2):
    """
        :param t1: Text string 1
        :param t2: Text String 2
        :return: Returns the Partial Token Sort Ratio score between the two given text

        Function to calculate the ratio of??????????????????????????

        Example : "" and "" returns a score of :
    """
    return fuzz.partial_token_sort_ratio(t1, t2)


def qRatio(t1, t2):
    """
        :param t1: Text string 1
        :param t2: Text String 2
        :return: Returns the Q Ratio score between the two given text

        Function to calculate the ratio of??????????????????????????

        Example : "" and "" returns a score of :
    """
    return fuzz.QRatio(t1, t2)


def wRatio(t1, t2):
    """
        :param t1: Text string 1
        :param t2: Text String 2
        :return: Returns the W Ratio score between the two given text

        Function to calculate the ratio of??????????????????????????

        Example : "" and "" returns a score of :
    """
    return fuzz.WRatio(t1, t2)
