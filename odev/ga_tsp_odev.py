import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

# Excel'den veriyi çekiyoruz
file_path = 'distance_matrix.xlsx'
df = pd.read_excel(file_path, header=None)
# Görseldeki gibi 0-20 arası değerleri alıyoruz
dist_matrix = df.iloc[1:22, 1:22].values.astype(float)

# Ayarlar
POP_SIZE = 100
GEN_LIMIT = 200
MUT_RATE = 0.1
ELITISM = 2
nodes = list(range(1, 21))  # 0 başlangıç olduğu için 1-20 arası gezilecek


def calc_dist(route):
    path = [0] + route + [0]
    total = 0
    for i in range(len(path) - 1):
        total += dist_matrix[int(path[i])][int(path[i + 1])]
    return total


def crossover(p1, p2):
    # Ordered Crossover: TSP için çakışma olmasın diye
    size = len(p1)
    a, b = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[a:b] = p1[a:b]

    p2_remain = [item for item in p2 if item not in child]
    idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = p2_remain[idx]
            idx += 1
    return child


def mutate(ind):
    # Inversion mutation: Bir parçayı ters çeviriyoruz
    if random.random() < MUT_RATE:
        a, b = sorted(random.sample(range(len(ind)), 2))
        ind[a:b] = ind[a:b][::-1]
    return ind


# İlk popülasyon
pop = [random.sample(nodes, len(nodes)) for _ in range(POP_SIZE)]
history = []

for gen in range(1, GEN_LIMIT + 1):
    pop = sorted(pop, key=lambda x: calc_dist(x))
    best_d = calc_dist(pop[0])
    best_r = [0] + pop[0] + [0]
    history.append(best_d)

    # Hoca bu formatı istemişti
    print(f"Iteration {gen} -> Best Distance: {best_d:.2f}")
    print(f"Best Route: {best_r}")
    print("-" * 20)

    new_pop = pop[:ELITISM]
    while len(new_pop) < POP_SIZE:
        parent1, parent2 = random.sample(pop[:20], 2)
        child = crossover(parent1, parent2)
        new_pop.append(mutate(child))
    pop = new_pop

# Sonuç Grafiği
plt.plot(history)
plt.title("Mesafe Gelişimi")
plt.xlabel("Nesil")
plt.ylabel("Mesafe")
plt.show()