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



