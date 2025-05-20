def ground(keywords, contract):
    return set(v for v in keywords if v in contract)


def measure_naive_precision_recall(contract: str, true_keywords: list[str], pred_keywords: list[str]):
    """
    Given the contract text, ground-truth keywords (info), and predicted keywords, naively compute precision & recall.
    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)
    Naively, because set intersection (with exact equality comparisons) is used. It is possible that some predicted keywords are substrings of the true keywords, or vice versa.
    Thus naive precision & recall are a lower bound on the actual precision & recall.
    """

    true_keywords = ground(true_keywords, contract)
    pred_keywords = ground(pred_keywords, contract)

    precision = len(pred_keywords.intersection(true_keywords)) / len(pred_keywords)
    recall = len(pred_keywords.intersection(true_keywords)) / len(true_keywords)

    return precision, recall


def redact(contract: str, keywords: list[str]):
    for keyword in keywords:
        contract = contract.replace(keyword, "████████")
    return contract


def measure_redaction_precision_recall(contract: str, true_keywords: list[str], pred_keywords: list[str]):
    """
    Precision & recall wrt redaction.
    Recall: how many true keywords are redacted? -- in other words, how many true keywords were not missed in the redaction?
    Precision: how many redacted keywords are true keywords? -- how much of the blacked-out text is actually true keywords?
    """
    assert true_keywords, "true_keywords must not be empty"
    true_keywords = ground(true_keywords, contract)
    pred_keywords = ground(pred_keywords, contract)

    contract_redacted = redact(contract, pred_keywords)

    missed_true_keywords = sum(int(true_keyword in contract_redacted) for true_keyword in true_keywords)
    recall = 1 - missed_true_keywords / len(true_keywords)

    # per pred_keyword, check if any true keyword is in it
    precision = sum(int(any(bool(true_keyword in pred_keyword) for true_keyword in true_keywords)) for pred_keyword in pred_keywords) / len(pred_keywords)

    return precision, recall

