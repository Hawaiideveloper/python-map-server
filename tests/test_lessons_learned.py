import os


def test_lessons_learned_contains_ghcr_entry():
    path = os.path.join(os.path.dirname(__file__), '..', 'Lessons_learned.md')
    path = os.path.abspath(path)
    assert os.path.exists(path), "Lessons_learned.md not found"

    with open(path, 'r') as f:
        content = f.read()

    assert 'GHCR 403 Forbidden' in content or 'GHCR 403' in content or '403 Forbidden' in content, (
        "Expected GHCR 403 lesson entry in Lessons_learned.md"
    )
