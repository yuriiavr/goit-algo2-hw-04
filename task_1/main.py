import sys
from collections import defaultdict, deque

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INF = 10**9

EDGES = [
    ("Термінал 1", "Склад 1", 25),
    ("Термінал 1", "Склад 2", 20),
    ("Термінал 1", "Склад 3", 15),
    ("Термінал 2", "Склад 3", 15),
    ("Термінал 2", "Склад 4", 30),
    ("Термінал 2", "Склад 2", 10),
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
    capacity = defaultdict(lambda: defaultdict(int))

    for u, v, cap in EDGES:
        capacity[u][v] += cap

    # суперджерело та суперстік для зведення задачі до одного джерела й стоку
    for terminal in TERMINALS:
        capacity[SUPER_SOURCE][terminal] = INF
    for store in STORES:
        capacity[store][SUPER_SINK] = INF

    return capacity


def edmonds_karp(capacity, source, sink, trace=None):
    residual = defaultdict(lambda: defaultdict(int))
    for u in capacity:
        for v in capacity[u]:
            residual[u][v] += capacity[u][v]
            residual[v][u] += 0

    max_flow = 0

    while True:
        # BFS шукає найкоротший збільшуючий шлях у залишковій мережі
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
            break

        path_flow = INF
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u

        if trace is not None:
            path = [sink]
            v = sink
            while v != source:
                v = parent[v]
                path.append(v)
            trace.append((list(reversed(path)), path_flow))

        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u

        max_flow += path_flow

    flow = defaultdict(lambda: defaultdict(int))
    for u, v, _ in EDGES:
        flow[u][v] = capacity[u][v] - residual[u][v]

    return max_flow, flow


def decompose_terminal_to_store(flow):
    """Розкладає потік на маршрути Термінал -> Склад -> Магазин."""
    result = defaultdict(int)

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

    print(f"Покроковий розрахунок ({len(trace)} збільшуючих шляхів):")
    for i, (path, amount) in enumerate(trace, 1):
        readable = [node for node in path if node not in (SUPER_SOURCE, SUPER_SINK)]
        print(f"  Крок {i:>2}: {' -> '.join(readable)}  (+{amount})")
    print()

    print("Потік Термінал -> Склад:")
    for t in TERMINALS:
        for w in WAREHOUSES:
            if flow[t][w] > 0:
                print(f"  {t:<12} -> {w:<10}: {flow[t][w]:>3}")
    print()

    print("Потік Склад -> Магазин:")
    for w in WAREHOUSES:
        for m in STORES:
            if flow[w][m] > 0:
                print(f"  {w:<10} -> {m:<11}: {flow[w][m]:>3}")
    print()

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
