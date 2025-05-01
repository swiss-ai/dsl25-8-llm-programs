from .templates import *
from llm_programs.programs.base import LMFunction, lines_parser
from llm_programs.utils import printw, wrap

from pprint import pformat


def generate_info(engine):
    lm_fn = LMFunction(engine=engine, parser=lines_parser)
    institutions = lm_fn(TEMPLATE_GEN_INSTITUTIONS)
    names = lm_fn(TEMPLATE_GEN_NAMES)
    phones = lm_fn(TEMPLATE_GEN_PHONES)
    faxes = lm_fn(TEMPLATE_GEN_FAXES)
    addresses = lm_fn(TEMPLATE_GEN_ADDRESSES)
    dates = lm_fn(TEMPLATE_GEN_DATES)
    emails = lm_fn(TEMPLATE_GEN_EMAILS.format(names, institutions))
    ips = lm_fn(TEMPLATE_GEN_IPS)
    networks = lm_fn(TEMPLATE_GEN_DOMAINS.format(institutions))
    prices = lm_fn(TEMPLATE_GEN_PRICES)

    return {
        "institutions": institutions,
        "names": names,
        "phones": phones,
        "faxes": faxes,
        "addresses": addresses,
        "dates": dates,
        "emails": emails,
        "ips": ips,
        "networks": networks,
        "prices": prices,
    }


def generate_description(engine, info):
    lm_fn = LMFunction(engine=engine)
    return lm_fn(TEMPLATE_GEN_DESCRIPTION.format(pformat(info, sort_dicts=False)))


def generate_contract_from_description(engine, info, description):
    lm_fn = LMFunction(engine=engine)
    return lm_fn(TEMPLATE_GEN_CONTRACT.format(info, description))
    

def dprint(label, text):
    print(label.upper())
    print("===============")
    print(text)
    print("---------------")
    print()


def generate_contract_aux(engine, debug=False):
    info = generate_info(engine)
    if debug: dprint("info", pformat(info, sort_dicts=False))
    description = generate_description(engine, info)
    if debug: dprint("description", wrap(description))
    contract = generate_contract_from_description(engine, info, description)
    if debug: dprint("contract", wrap(contract))
    return info, description, contract


def generate_contract_only(*args, **kwargs):
    return generate_contract_aux(*args, **kwargs)[-1]


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

