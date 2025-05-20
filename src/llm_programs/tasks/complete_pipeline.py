from pathlib import Path
import re

import logging
from typing import Iterable

from llm_programs.utils import DocumentDirectory, DocumentTransform
from llm_programs.tasks.redaction.eval import one_call_m_prompts_fn, unionize_windows


MD_TABLE_REGEX = re.compile(r"((?:\| *[^|\r\n]+ *)+\|)(?:\r?\n)((?:\|[ :]?-+[ :]?)+\|)((?:(?:\r?\n)(?:\| *[^|\r\n]+ *)+\|)+)")


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
# source: https://gist.github.com/gruber/8891611
WEB_URL_REGEX = re.compile(r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))")
IPV4_REGEX = re.compile(r"((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}")

REDACTION_PATTERNS = [
    EMAIL_REGEX,
    WEB_URL_REGEX,
    IPV4_REGEX,
]


# Keywords that should *not* be redacted
WHITELIST = [
    "None",
    "Institution",
    "University",
    "Publisher",
    "Publication",
    "```",
]

def whitelisted(keyword: str) -> bool:
    if keyword in WHITELIST:
        return True
    if re.fullmatch(r"[0-9]{1,2}\.?", keyword) is not None:
        return True
    if len(keyword) < 2:
        return True
    return False
    

def clean_keywords(keywords: Iterable[str]) -> list[str]:
    return [k.strip() for k in keywords if k.strip()]


def load_manual_keywords() -> list[str]:
    inst_file = Path('./data/contracts/confidential/institutions.txt')
    inst_keywords = [val.strip()
                     for line in inst_file.read_text().splitlines()
                     for val in line.split(';')]
    # logger.debug(f"{inst_keywords=}")
    special_file = Path('./data/contracts/confidential/special.txt')
    special_keywords = [line.strip()
                        for line in special_file.read_text().splitlines()]
    manual_keywords = inst_keywords + special_keywords
    manual_keywords = clean_keywords(manual_keywords)
    return manual_keywords


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def main():
    parent_dir = Path('./data/contracts/confidential/')
    dd = DocumentDirectory(parent_dir / 'contracts_1_markerpdf')

    def make_clean(path: Path) -> DocumentDirectory:
        transform = DocumentTransform(dd, path)

        def clean_fn(document):
            content = document.read()
            # Remove tables
            new_content = re.sub(MD_TABLE_REGEX, "", content)
            # Remove <br> tags
            new_content = new_content.replace('<br>', '')
            # Remove image descriptions
            new_content = re.sub(r'^Image /page.*$', '', new_content, flags=re.MULTILINE)
            # Remove repeated dots
            new_content = re.sub(r'\.{10,}', '', new_content)
            return new_content

        dd_clean = transform.apply(clean_fn)
        return dd_clean

    dd_clean = DocumentDirectory.find_or_make(parent_dir / 'contracts_2_clean', make_clean)

    window_size = 4_000
    window_stride = window_size - 100

    def make_redacted(path: Path) -> DocumentDirectory:

        def redact_fn(document):
            logger.info(f"Redacting {document.name}")
            md_file = document.md_file
            kw_file = path / md_file.stem / md_file.name.replace('.md', '.keywords.md')
            logger.info(kw_file)
            if kw_file.exists():
                logger.info(f"Found keywords file: {kw_file}")
                keywords = kw_file.read_text().splitlines()
            else:
                logger.info(f"Generating keywords for {document.name}")
                keywords_set: set[str] = unionize_windows(one_call_m_prompts_fn, document, size=window_size, stride=window_stride)
                keywords: list[str] = clean_keywords(keywords_set)
            re_matches = []
            content = document.read()
            for regex in REDACTION_PATTERNS:
                re_matches.extend(regex.findall(content))
            keywords_ = [k for k in keywords if not whitelisted(k)]
            keywords_ += load_manual_keywords()
            new_content = document.redact(keywords_, REDACTION_PATTERNS)
            aux = {
                "keywords": '\n'.join(keywords),
                "re_matches": repr(re_matches),
            }
            return new_content, aux
        
        dd_redacted = DocumentTransform(dd_clean, path).apply(redact_fn, aux=True, exist_ok=True)

        # TODO upload to gitlab
        return dd_redacted

    dd_redacted = make_redacted(parent_dir / 'contracts_3_redacted')


if __name__ == "__main__":
    main()