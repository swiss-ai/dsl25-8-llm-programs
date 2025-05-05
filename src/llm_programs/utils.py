from pathlib import Path


import re
import random
import textwrap
import pickle

from typing import Dict, Iterable, Callable, NamedTuple
from functools import reduce, wraps

import logging
logger = logging.getLogger(__name__)


PAGE_DELIMETER = re.compile(r'\n*\{\d+\}-{48}\n*')

IDENTITY = lambda x: x


class DocumentEntry(NamedTuple):
    """Represents data for a single directory entry."""
    name: str          # Base name for directory and files
    main_text: str     # Content for the main .md file
    aux_files: Dict[str, str] # Auxiliary file key -> content mapping


class DocumentDirectory():
    """
    A directory of subdirectories with .md files, in the structure of marker-pdf output.
    """
    def __init__(self, path):
        self.path = Path(path)

    def __repr__(self):
        return f"DocumentDirectory({self.path})"

    @staticmethod
    def from_md_files(path: Path, md_paths: Iterable[Path], debug=False):
        """Make a DocumentDirectory from .md files"""
        return DocumentDirectory.from_md_texts(path, ((md_path.stem, md_path.read_content()) for md_path in md_paths))
                                               
    @staticmethod
    def from_md_texts(path: Path, entries):
        """Make a DocumentDirectory from .md texts"""
        return DocumentDirectory.from_md_texts_aux(path, (DocumentEntry(md_name, md_text, {}) for md_name, md_text in entries))
   
    def from_md_texts_aux(path: Path, entries: Iterable[DocumentEntry]):
        path.mkdir(parents=True, exist_ok=False)
        for md_name, md_text, kwargs in entries:
            print(f"{md_name=}")
            print(f"md_text={md_text[:100]}")
            print(f"{kwargs=}")
            (path / md_name).mkdir(parents=True, exist_ok=False)
            logger.debug(f"mk_from_md_texts: writing main to {path / md_name / f'{md_name}.md'}")
            (path / md_name / f"{md_name}.md").write_text(md_text)
            for kw in kwargs:
                aux_text = kwargs[kw]
                print(f"aux_text={aux_text}")
                logger.debug(f"mk_from_md_texts: writing {kw} to {path / md_name / f'{md_name}.{kw}.md'}")
                (path / md_name / f"{md_name}.{kw}.md").write_text(aux_text)
        return DocumentDirectory(path)

    @staticmethod
    def find_or_make(path: Path, fn: callable):
        if path.exists():
            return DocumentDirectory(path)
        else:
            return fn(path)

    def docs(self):
        """
        Iterate over subdirectories/docs
        """
        for subdir in self.path.iterdir():
            if subdir.is_dir():
                yield Document(subdir)
    
    def get_total_n_pages(self):
        return sum(doc.get_n_pages() for doc in self.docs())

    def get_total_n_chars(self):
        return sum(doc.get_n_chars() for doc in self.docs())

    def __hash__(self):
        return hash(self.path)



class Document():
    """
    An .md document, in a subdirectory of the same name
    """
    def __init__(self, subdir):
        self.subdir = subdir
        assert subdir.is_dir(), f"Expected a directory, got {subdir}"
        name = subdir.name
        self.name = name
        self.md_file = subdir / f"{name}.md"
        assert self.md_file.exists(), f"Document {self.md_file} does not exist"

    def __repr__(self):
        return f'Doc("{self.md_file.stem}")'

    def read(self):
        return self.md_file.read_text()

    def read_aux(self, aux_name):
        return (self.subdir / f"{self.name}.{aux_name}.md").read_text()

    def pages(self, enum=False, min_n_chars=10):
        content = self.read()
        for i, page in enumerate(re.split(PAGE_DELIMETER, content), start=-1):
            if i == -1 or len(page) < min_n_chars:
                continue
            if enum:
                yield i, page.strip()
            else:
                yield page.strip()
        
    def windows(self, size=1000, stride=900):
        """
        Yield windows of size `size` with stride `stride`
        """
        content = self.read()
        content = re.sub(PAGE_DELIMETER, '\n\n', content)
        content = re.sub(r"\n{2,}", "\n\n", content)
        for i in range(0, len(content), stride):
            yield content[i:i+size]

    def get_n_pages(self):
        return sum(1 for _ in self.pages())

    def get_n_chars(self):
        return sum(len(page) for page in self.pages())
    
    def __hash__(self):
        return hash(self.md_file)

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)


class DocumentTransform():
    """
    A helper to execute transforms on a DocDir
    """
    def __init__(self, src: DocumentDirectory, dest_path: Path):
        self.src = src
        self.dest_path = Path(dest_path)

    def __repr__(self):
        return f"DocTransform({self.src.name}, {self.dest_path.name})"

    def apply(self, func: Callable[[str], [str]], debug=False):
        """
        Apply a function to each document in the directory
        """
        assert self.src.path.exists(), f"Source directory {self.src.path} does not exist"
        assert not self.dest_path.exists(), f"Destination directory {self.dest_path} already exists"
        return DocumentDirectory.from_md_texts(self.dest_path,
                                               ((doc.md_file.stem, func(doc.read())) for doc in self.src.docs()))


Doc = Document
DocDir = DocumentDirectory
DocTransform = DocumentTransform


def make_sample_docdir(src, dest_path, n=10, seed=None):
    if seed is not None:
        random.seed(seed)
    docs = list(src.docs())
    docs_sample = random.sample(docs, min(n, len(docs)))
    md_paths = [doc.md for doc in docs_sample]
    return DocumentDirectory.from_md_files(dest_path, md_paths)
    

def printw(text, **kw):
    print(wrap(text, **kw))


def wrap(text, width=200):
    return textwrap.fill(text, width=width, replace_whitespace=False)


def debug_wrap(engine):
    '''TODO fix'''
    def wrapped(prompt):
        print(f"==== Prompt ====")
        print(prompt)
        print(f"================")
        response = engine(prompt)
        print(f"=== Response ===")
        print(response)
        print(f"================")
        return response
    return wrapped


def flat(nested_list: list[list]) -> list:
    """
    Flatten a nested list.
    """
    return [item for sublist in nested_list for item in sublist]


def unionize(nested_list: list[list]) -> set:
    return reduce(set.union, map(set, nested_list))


save = lambda obj, path: pickle.dump(obj, open(path, 'wb'))

load = lambda path: pickle.load(open(path, 'rb'))


def debug_wrap(engine_func):
    @wraps(engine_func)
    def wrapped(self, prompt):
        print(f"==== Prompt ====")
        print(prompt)
        print(f"================")
        
        response = engine_func(self, prompt)
        
        print(f"=== Response ===")
        print(response)
        print(f"================")
        
        return response

    return wrapped