import time


def words_load(word_len: int, file_path: str) -> list[str]:
    """Load words from vocabulary file."""
    words = []
    file_name = f"{file_path}words{word_len}.txt"
    with open(file_name, "r", encoding="utf-8") as fh:
        for word in fh:
            words.append(word.strip("\r\n\t "))
    return words


def millis(start_time: int) -> int:
    """Return time in milliseconds."""
    return int(round((time.time() - start_time) * 1000.0, 0))
