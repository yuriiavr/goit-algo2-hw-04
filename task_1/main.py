"""Завдання 1. Алгоритм максимального потоку (Едмондса–Карпа) для логістики.

Програма будує орієнтований граф логістичної мережі:

    Термінали  ->  Склади  ->  Магазини

та знаходить максимальний потік товарів від терміналів до магазинів за
допомогою алгоритму Едмондса–Карпа (BFS-реалізація методу Форда–Фалкерсона,
що завжди шукає найкоротший збільшуючий шлях у залишковій мережі).

Оскільки джерел (терміналів) і стоків (магазинів) декілька, до графа додаються
фіктивне суперджерело ``S`` та суперстік ``T``. Це класичний прийом, який
дозволяє звести задачу з кількома джерелами/стоками до стандартної задачі
максимального потоку з одним джерелом та одним стоком.
"""

import sys
from collections import defaultdict, deque

# У Windows-консолі типове кодування часто cp1251/cp866 — переходимо на UTF-8,
# щоб кирилиця у виводі відображалася коректно.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# "Нескінченна" пропускна здатність для ребер суперджерела/суперстоку.
INF = 10**9


# ---------------------------------------------------------------------------
# Опис логістичної мережі (ребра та пропускні здатності з умови задачі)
# ---------------------------------------------------------------------------
EDGES = [
    # Термінал -> Склад
    ("Термінал 1", "Склад 1", 25),
    ("Термінал 1", "Склад 2", 20),
    ("Термінал 1", "Склад 3", 15),
    ("Термінал 2", "Склад 3", 15),
    ("Термінал 2", "Склад 4", 30),
    ("Термінал 2", "Склад 2", 10),
    # Склад -> Магазин
    ("Склад 1", "Магазин 1", 15),
    ("Склад 1", "Магазин 2", 10),
    ("Склад 1", "Магазин 3", 20),
    ("Склад 2", "Магазин 4", 15),
    ("Склад 2", "Магазин 5", 10),
    ("Склад 2", "Магазин 6", 25),
    ("Склад 3", "Магазин 7", 20),
    ("Склад 3", "Магазин 8", 15),
    ("Склад 3", "Магазин 9", 10),
    ("Склад 4", "Магазин 10", 20),
    ("Склад 4", "Магазин 11", 10),
    ("Склад 4", "Магазин 12", 15),
    ("Склад 4", "Магазин 13", 5),
    ("Склад 4", "Магазин 14", 10),
]

TERMINALS = ["Термінал 1", "Термінал 2"]
WAREHOUSES = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
STORES = [f"Магазин {i}" for i in range(1, 15)]

SUPER_SOURCE = "S"
SUPER_SINK = "T"


def build_capacity():
    """Будує матрицю пропускних здатностей (dict-of-dict) з фіктивними S та T."""
    capacity = defaultdict(lambda: defaultdict(int))

    for u, v, cap in EDGES:
        capacity[u][v] += cap

    # Суперджерело -> кожен термінал (необмежено, реально обмежить вихід терміналу).
    for terminal in TERMINALS:
        capacity[SUPER_SOURCE][terminal] = INF

    # Кожен магазин -> суперстік (необмежено).
    for store in STORES:
        capacity[store][SUPER_SINK] = INF

    return capacity


def edmonds_karp(capacity, source, sink, trace=None):
    """Повертає (max_flow, flow), де flow[u][v] — фактичний потік по ребру u->v.

    Реалізація алгоритму Едмондса–Карпа: на кожній ітерації BFS шукає найкоротший
    (за кількістю ребер) збільшуючий шлях у залишковій мережі та проштовхує по
    ньому максимально можливий потік (вузьке місце шляху).

    Якщо передано список ``trace``, у нього додаються кортежі (шлях, обсяг) для
    кожного знайденого збільшуючого шляху — для покрокового звіту.
    """
    # Залишкова мережа: residual[u][v] — залишкова пропускна здатність ребра u->v.
    residual = defaultdict(lambda: defaultdict(int))
    for u in capacity:
        for v in capacity[u]:
            residual[u][v] += capacity[u][v]
            residual[v][u] += 0  # гарантуємо існування зворотного ребра

    max_flow = 0

    while True:
        # --- BFS: пошук найкоротшого збільшуючого шляху source -> sink ---
        parent = {source: source}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            if u == sink:
                break
            for v, residual_cap in residual[u].items():
                if v not in parent and residual_cap > 0:
                    parent[v] = u
                    queue.append(v)

        if sink not in parent:
            break  # збільшуючих шляхів більше немає -> потік максимальний

        # --- Вузьке місце знайденого шляху ---
        path_flow = INF
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u

        # --- Відновлення шляху (для трасування) ---
        if trace is not None:
            path = [sink]
            v = sink
            while v != source:
                v = parent[v]
                path.append(v)
            trace.append((list(reversed(path)), path_flow))

        # --- Оновлення залишкової мережі вздовж шляху ---
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u

        max_flow += path_flow

    # Фактичний потік по кожному вихідному ребру = пропускна здатність - залишок.
    flow = defaultdict(lambda: defaultdict(int))
    for u, v, _ in EDGES:
        flow[u][v] = capacity[u][v] - residual[u][v]

    return max_flow, flow


def decompose_terminal_to_store(flow):
    """Розкладає потік на маршрути Термінал -> Склад -> Магазин.

    Для кожного складу виконується баланс: сума вхідного потоку від терміналів
    дорівнює сумі вихідного потоку до магазинів. Жадібно зіставляємо вхідні
    «порції» від терміналів з вихідними до магазинів, отримуючи фактичний потік
    для кожної пари (Термінал, Магазин).
    """
    result = defaultdict(int)  # (термінал, магазин) -> обсяг

    for w in WAREHOUSES:
        inflow = {t: flow[t][w] for t in TERMINALS if flow[t][w] > 0}
        outflow = {m: flow[w][m] for m in STORES if flow[w][m] > 0}

        for t in list(inflow):
            for m in list(outflow):
                if inflow[t] == 0:
                    break
                if outflow[m] == 0:
                    continue
                amount = min(inflow[t], outflow[m])
                result[(t, m)] += amount
                inflow[t] -= amount
                outflow[m] -= amount

    return result


def print_report(max_flow, flow, terminal_store_flow, trace):
    print("=" * 60)
    print("ЛОГІСТИЧНА МЕРЕЖА — МАКСИМАЛЬНИЙ ПОТІК (Едмондс–Карп)")
    print("=" * 60)
    print(f"\nМаксимальний потік у мережі: {max_flow} одиниць\n")

    # --- Покроковий розрахунок: збільшуючі шляхи ---
    print(f"Покроковий розрахунок ({len(trace)} збільшуючих шляхів):")
    for i, (path, amount) in enumerate(trace, 1):
        # Прибираємо фіктивні вузли S та T для читабельності.
        readable = [node for node in path if node not in (SUPER_SOURCE, SUPER_SINK)]
        print(f"  Крок {i:>2}: {' -> '.join(readable)}  (+{amount})")
    print()

    # --- Потоки по ребрах Термінал -> Склад ---
    print("Потік Термінал -> Склад:")
    for t in TERMINALS:
        for w in WAREHOUSES:
            if flow[t][w] > 0:
                print(f"  {t:<12} -> {w:<10}: {flow[t][w]:>3}")
    print()

    # --- Потоки по ребрах Склад -> Магазин ---
    print("Потік Склад -> Магазин:")
    for w in WAREHOUSES:
        for m in STORES:
            if flow[w][m] > 0:
                print(f"  {w:<10} -> {m:<11}: {flow[w][m]:>3}")
    print()

    # --- Підсумкова таблиця Термінал -> Магазин ---
    print("=" * 60)
    print(f"{'Термінал':<12} {'Магазин':<12} {'Фактичний Потік (одиниць)':>26}")
    print("-" * 60)
    total = 0
    for t in TERMINALS:
        for m in STORES:
            value = terminal_store_flow.get((t, m), 0)
            if value > 0:
                print(f"{t:<12} {m:<12} {value:>26}")
                total += value
    print("-" * 60)
    print(f"{'РАЗОМ':<25} {total:>26}")
    print("=" * 60)


def main():
    capacity = build_capacity()
    trace = []
    max_flow, flow = edmonds_karp(capacity, SUPER_SOURCE, SUPER_SINK, trace=trace)
    terminal_store_flow = decompose_terminal_to_store(flow)
    print_report(max_flow, flow, terminal_store_flow, trace)


if __name__ == "__main__":
    main()
