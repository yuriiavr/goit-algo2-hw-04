"""Завдання 2. Розширення функціоналу префіксного дерева (Trie).

Клас ``Homework`` наслідує базовий ``Trie`` та додає два методи:

* ``count_words_with_suffix(pattern)`` — кількість слів, що закінчуються на
  заданий шаблон ``pattern`` (з урахуванням регістру);
* ``has_prefix(prefix)`` — чи існує хоча б одне слово із заданим префіксом
  ``prefix`` (з урахуванням регістру).

Обидва методи валідовують вхідні дані: приймають лише рядки, інакше піднімають
``TypeError``.
"""

from trie import Trie


class Homework(Trie):
    def count_words_with_suffix(self, pattern) -> int:
        """Повертає кількість слів у дереві, що закінчуються на ``pattern``.

        Враховує регістр символів. Якщо таких слів немає — повертає 0.
        Порожній рядок є суфіксом будь-якого слова, тож повертається загальна
        кількість слів.

        Складність: O(N) обходу дерева, де N — кількість вузлів; для кожного
        слова порівняння суфікса коштує O(len(pattern)). Завдяки тому, що під
        час обходу зберігаються лише останні ``len(pattern)`` символів шляху,
        пам'ять не зростає з довжиною слів.
        """
        if not isinstance(pattern, str):
            raise TypeError(
                f"Illegal argument: pattern = {pattern} must be a string"
            )

        # Порожній суфікс підходить усім словам.
        if pattern == "":
            return self.size

        suffix_len = len(pattern)
        count = 0

        # Ітеративний обхід у глибину; tail — кортеж останніх ≤ suffix_len
        # символів поточного шляху від кореня.
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
        """Повертає ``True``, якщо існує хоча б одне слово з префіксом ``prefix``.

        Враховує регістр символів. Порожній префікс вважається префіксом будь-
        якого слова, тож метод повертає ``True`` за наявності хоча б одного слова.

        Складність: O(len(prefix)) на спуск до вузла префікса; пошук першого
        слова в піддереві завершується достроково, тож фактично O(len(prefix) +
        довжина найкоротшого слова з цим префіксом).
        """
        if not isinstance(prefix, str):
            raise TypeError(
                f"Illegal argument: prefix = {prefix} must be a string"
            )

        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]

        # Вузол префікса існує — перевіряємо, що в його піддереві є хоча б одне
        # слово (достроковий вихід на першому ж знайденому).
        return self._has_any_word(current)

    @staticmethod
    def _has_any_word(node) -> bool:
        """Чи містить піддерево з коренем ``node`` хоча б одне слово."""
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

    # --- Додаткові перевірки крайових випадків ---
    # Відсутній суфікс -> 0
    assert trie.count_words_with_suffix("xyz") == 0
    # Урахування регістру: великі літери не збігаються з рядковими
    assert trie.count_words_with_suffix("E") == 0
    assert trie.has_prefix("App") is False
    # Порожній суфікс -> усі слова; порожній префікс -> True (є слова)
    assert trie.count_words_with_suffix("") == 4
    assert trie.has_prefix("") is True
    # Цілий рядок як суфікс
    assert trie.count_words_with_suffix("banana") == 1

    # --- Опрацювання некоректних вхідних даних ---
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
