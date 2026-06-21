from trie import Trie


class Homework(Trie):
    def count_words_with_suffix(self, pattern) -> int:
        if not isinstance(pattern, str):
            raise TypeError(
                f"Illegal argument: pattern = {pattern} must be a string"
            )

        if pattern == "":
            return self.size

        suffix_len = len(pattern)
        count = 0

        # обхід дерева, зберігаємо лише останні suffix_len символів шляху
        stack = [(self.root, ())]
        while stack:
            node, tail = stack.pop()
            if (
                node.value is not None
                and len(tail) == suffix_len
                and "".join(tail) == pattern
            ):
                count += 1
            for char, child in node.children.items():
                new_tail = (tail + (char,))[-suffix_len:]
                stack.append((child, new_tail))

        return count

    def has_prefix(self, prefix) -> bool:
        if not isinstance(prefix, str):
            raise TypeError(
                f"Illegal argument: prefix = {prefix} must be a string"
            )

        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]

        return self._has_any_word(current)

    @staticmethod
    def _has_any_word(node) -> bool:
        stack = [node]
        while stack:
            current = stack.pop()
            if current.value is not None:
                return True
            stack.extend(current.children.values())
        return False


if __name__ == "__main__":
    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    # Перевірка кількості слів, що закінчуються на заданий суфікс
    assert trie.count_words_with_suffix("e") == 1  # apple
    assert trie.count_words_with_suffix("ion") == 1  # application
    assert trie.count_words_with_suffix("a") == 1  # banana
    assert trie.count_words_with_suffix("at") == 1  # cat

    # Перевірка наявності префікса
    assert trie.has_prefix("app") == True  # apple, application
    assert trie.has_prefix("bat") == False
    assert trie.has_prefix("ban") == True  # banana
    assert trie.has_prefix("ca") == True  # cat

    # Крайові випадки та урахування регістру
    assert trie.count_words_with_suffix("xyz") == 0
    assert trie.count_words_with_suffix("E") == 0
    assert trie.has_prefix("App") is False
    assert trie.count_words_with_suffix("") == 4
    assert trie.has_prefix("") is True
    assert trie.count_words_with_suffix("banana") == 1

    # Некоректні вхідні дані
    for bad in (None, 123, ["a"], 3.14):
        try:
            trie.count_words_with_suffix(bad)
            raise AssertionError(f"Очікувався TypeError для {bad!r}")
        except TypeError:
            pass
        try:
            trie.has_prefix(bad)
            raise AssertionError(f"Очікувався TypeError для {bad!r}")
        except TypeError:
            pass

    print("Усі перевірки пройдено успішно!")
