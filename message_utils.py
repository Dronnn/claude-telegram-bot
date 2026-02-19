from __future__ import annotations

TELEGRAM_MESSAGE_LIMIT = 4096


def split_message(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break

        # Try to split on last newline within limit
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit  # Hard split
            parts.append(text[:cut])
            text = text[cut:]
        else:
            parts.append(text[:cut])
            text = text[cut + 1:]  # skip the newline

    return parts
