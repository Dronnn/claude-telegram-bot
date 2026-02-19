from message_utils import split_message

LIMIT = 4096


def test_short_message_unchanged():
    text = "Hello, world!"
    result = split_message(text, LIMIT)
    assert result == ["Hello, world!"]


def test_empty_message():
    result = split_message("", LIMIT)
    assert result == [""]


def test_exact_limit():
    text = "a" * LIMIT
    result = split_message(text, LIMIT)
    assert result == [text]


def test_split_on_newline():
    line = "x" * 100 + "\n"
    text = line * 50  # 5050 chars, > 4096
    result = split_message(text, LIMIT)
    assert len(result) == 2
    for part in result:
        assert len(part) <= LIMIT
        assert not part.startswith("\n")


def test_long_single_line():
    text = "x" * 8000  # No newlines, must hard-split
    result = split_message(text, LIMIT)
    assert len(result) == 2
    assert len(result[0]) == LIMIT
    assert len(result[1]) == 8000 - LIMIT


def test_preserves_all_content():
    lines = [f"Line {i}\n" for i in range(200)]
    text = "".join(lines)
    result = split_message(text, LIMIT)
    # Newlines at split boundaries are consumed as separators,
    # so rejoin with newline and verify no content lines are lost.
    reassembled = "\n".join(result)
    assert reassembled == text
