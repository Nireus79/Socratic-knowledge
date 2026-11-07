> **Proof of concept, not a product.** This library belongs to the earlier Python research prototype ([Socrates](https://github.com/Nireus79/Socrates)) and is not maintained as a product. The current products are listed at [nireus79.github.io](https://nireus79.github.io/). Contact: Hermes_creative@proton.me.

# Socratic Knowledge

[![PyPI](https://img.shields.io/pypi/v/socratic-knowledge)](https://pypi.org/project/socratic-knowledge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A small package extracted from the Socrates prototype. It has no dependencies outside the Python standard library.

## What is in the package

- `KnowledgeEntry`: a dataclass (`id`, `content`, `category`, `embedding`, `metadata`) with `to_dict()` and `from_dict()`.
- `CodeParser`: reads the structure of a source file from its text. Python files are parsed with the `ast` module; JavaScript, Java, C and C++ files with regular expressions, so those results are approximate.
- `DEFAULT_KNOWLEDGE`: a list of five general notes (software architecture, Python practice and similar) that the prototype used as starting entries.

There is no storage, no search, no access control, no versioning, no multi-tenancy and no audit log. Earlier versions of this README described a `KnowledgeManager` with those features; it does not exist in the code. For vector search over entries like these, see [socratic-rag](https://github.com/Nireus79/Socratic-rag).

## Install

```bash
pip install socratic-knowledge
```

## Use

```python
from socratic_knowledge import CodeParser, KnowledgeEntry

source = """
import os

class Greeter:
    def hello(self, name):
        return "hi " + name

def main():
    pass
"""

result = CodeParser().parse_file("greeter.py", source)
print(result["language"])            # python
print(result["structure_summary"])   # one-line summary
print([c["name"] for c in result["classes"]])      # ['Greeter']
print([f["name"] for f in result["functions"]])    # ['main']

entry = KnowledgeEntry(id="greeter", content=result["structure_summary"], category="code")
print(entry.to_dict())
```

`parse_file` returns a dictionary with `language`, `file_path`, `functions`, `classes`, `imports`, `structure_summary` and `metrics` (line, function, class and import counts). An unsupported file extension is reported in the result and is not parsed.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/
```

## License

MIT. Contact: Hermes_creative@proton.me
