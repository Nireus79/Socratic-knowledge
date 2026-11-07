"""Behaviour of the three things the package exports."""

from socratic_knowledge import DEFAULT_KNOWLEDGE, CodeParser, KnowledgeEntry


def test_entry_round_trip():
    entry = KnowledgeEntry(id="a", content="text", category="note", metadata={"k": 1})
    assert KnowledgeEntry.from_dict(entry.to_dict()) == entry


def test_parser_reads_python_structure():
    source = "import os\n\nclass A:\n    def f(self, x):\n        return x\n\ndef g():\n    pass\n"
    result = CodeParser().parse_file("a.py", source)
    assert result["language"] == "python"
    assert [c["name"] for c in result["classes"]] == ["A"]
    assert [f["name"] for f in result["functions"]] == ["g"]
    assert result["imports"] == ["os"]
    assert result["metrics"]["class_count"] == 1


def test_default_knowledge_entries_have_required_fields():
    assert DEFAULT_KNOWLEDGE
    for item in DEFAULT_KNOWLEDGE:
        assert {"id", "content", "category"} <= set(item)
