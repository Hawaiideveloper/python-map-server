import os


def test_checklist_exists_and_has_many_items():
    path = os.path.join(os.path.dirname(__file__), '..', 'checklist.md')
    path = os.path.abspath(path)
    assert os.path.exists(path), f"checklist.md not found at {path}"

    with open(path, 'r') as f:
        content = f.read()

    # simple heuristic: count checkboxes
    checks = content.count('- [ ]') + content.count('- [x]')
    assert checks >= 50, f"Expected 50+ checklist items, found {checks}"


def test_lessons_learned_exists():
    path = os.path.join(os.path.dirname(__file__), '..', 'Lessons_learned.md')
    assert os.path.exists(path), "Lessons_learned.md not found"


def test_claude_doc_exists():
    path = os.path.join(os.path.dirname(__file__), '..', 'Claude.md')
    assert os.path.exists(path), "Claude.md not found"
