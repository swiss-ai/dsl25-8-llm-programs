from pathlib import Path


import re
import random
import textwrap


PAGE_DELIMETER = re.compile(r'\n*\{\d+\}-{48}\n*')


class DocDir():
    """
    A directory of subdirectories with .md files, in the structure of marker-pdf output.
    """
    def __init__(self, path):
        self.path = Path(path)

    def __repr__(self):
        return f"DocDir({self.path})"

    @staticmethod
    def make(path: Path, md_paths: list[Path]):
        """Make a DocDir from of .md files"""
        path.mkdir(parents=True, exist_ok=False)
        for md_path in md_paths:
            subdir = path / md_path.stem
            subdir.mkdir(parents=True, exist_ok=False)
            new_md_path = subdir / md_path.name
            new_md_path.write_text(md_path.read_text())
        return DocDir(path)

    @staticmethod
    def find_or_make(path: Path, fn: callable):
        if path.exists():
            return DocDir(path)
        else:
            return fn(path)

    def docs(self):
        """
        Iterate over subdirectories/docs
        """
        for subdir in self.path.iterdir():
            if subdir.is_dir():
                yield Doc(subdir)
    
    def get_total_n_pages(self):
        return sum(doc.get_n_pages() for doc in self.docs())

    def get_total_n_chars(self):
        return sum(doc.get_n_chars() for doc in self.docs())

    def __hash__(self):
        return hash(self.path)



class Doc():
    """
    An .md document, in a subdirectory of the same name
    """
    def __init__(self, subdir):
        self.subdir = subdir
        assert subdir.is_dir(), f"Expected a directory, got {subdir}"
        name = subdir.name
        self.md = subdir / f"{name}.md"
        assert self.md.exists(), f"Document {self.md} does not exist"

    def __repr__(self):
        return f'Doc("{self.md.stem}")'

    def read(self):
        return read(self.md)

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
        return hash(self.md)

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)


class DocTransform():
    """
    A helper to execute transforms on a DocDir
    """
    def __init__(self, src: DocDir, dest_path: Path):
        self.src = src
        self.dest_path = Path(dest_path)

    def __repr__(self):
        return f"DocTransform({self.src.name}, {self.dest_path.name})"

    def apply(self, func, debug=False):
        """
        Apply a function to each document in the directory
        """
        assert self.src.path.exists(), f"Source directory {self.src.path} does not exist"
        assert not self.dest_path.exists(), f"Destination directory {self.dest_path} already exists"
        self.dest_path.mkdir(parents=True, exist_ok=False)
        for doc in self.src.docs():
            content = doc.read()
            new_content = func(content)
            new_path = self.dest_path / doc.subdir.name / doc.md.name
            new_path.parent.mkdir(parents=True, exist_ok=False)
            if debug:
                print(f"Writing {round(len(new_content)/len(content) * 100)}% to {new_path}")
            write(new_path, new_content)
        return DocDir(self.dest_path)


def make_sample_docdir(src, dest_path, n=10, seed=None):
    if seed is not None:
        random.seed(seed)
    docs = list(src.docs())
    docs_sample = random.sample(docs, min(n, len(docs)))
    md_paths = [doc.md for doc in docs_sample]
    return DocDir.make(dest_path, md_paths)
    

def read(file):
    with open(file, 'r') as f:
        return f.read()
    

def write(file, content):
    with open(file, 'w') as f:
        f.write(content)

def printw(text):
    print(wrap(text))

def wrap(text):
    return textwrap.fill(text, width=120, drop_whitespace=False, replace_whitespace=False)

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

