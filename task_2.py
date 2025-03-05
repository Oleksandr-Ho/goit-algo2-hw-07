import sys
import time
import matplotlib.pyplot as plt
from functools import lru_cache

##################################################
# 1. Класи для Splay Tree
##################################################

class Node:
    def __init__(self, key, value, parent=None):
        self.key = key
        self.value = value
        self.parent = parent
        self.left_node = None
        self.right_node = None

class SplayTree:
    def __init__(self):
        self.root = None

    def find(self, key):
        node = self.root
        while node is not None:
            if key < node.key:
                node = node.left_node
            elif key > node.key:
                node = node.right_node
            else:
                self._splay(node)
                return node.value
        return None

    def insert(self, key, value):
        if self.root is None:
            self.root = Node(key, value)
            return
        current = self.root
        while True:
            if key < current.key:
                if current.left_node:
                    current = current.left_node
                else:
                    current.left_node = Node(key, value, parent=current)
                    self._splay(current.left_node)
                    return
            elif key > current.key:
                if current.right_node:
                    current = current.right_node
                else:
                    current.right_node = Node(key, value, parent=current)
                    self._splay(current.right_node)
                    return
            else:
                current.value = value
                self._splay(current)
                return

    def _splay(self, node):
        while node.parent is not None:
            parent = node.parent
            grandparent = parent.parent
            if grandparent is None:
                # Zig
                if node == parent.left_node:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)
            else:
                # Zig-Zig або Zig-Zag
                if node == parent.left_node and parent == grandparent.left_node:
                    self._rotate_right(grandparent)
                    self._rotate_right(parent)
                elif node == parent.right_node and parent == grandparent.right_node:
                    self._rotate_left(grandparent)
                    self._rotate_left(parent)
                elif node == parent.right_node and parent == grandparent.left_node:
                    self._rotate_left(parent)
                    self._rotate_right(grandparent)
                else:
                    self._rotate_right(parent)
                    self._rotate_left(grandparent)

    def _rotate_right(self, node):
        left_child = node.left_node
        if not left_child:
            return
        node.left_node = left_child.right_node
        if left_child.right_node:
            left_child.right_node.parent = node
        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.left_node:
            node.parent.left_node = left_child
        else:
            node.parent.right_node = left_child
        left_child.right_node = node
        node.parent = left_child

    def _rotate_left(self, node):
        right_child = node.right_node
        if not right_child:
            return
        node.right_node = right_child.left_node
        if right_child.left_node:
            right_child.left_node.parent = node
        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left_node:
            node.parent.left_node = right_child
        else:
            node.parent.right_node = right_child
        right_child.left_node = node
        node.parent = right_child

##################################################
# 2. Функції Фібоначчі
##################################################

@lru_cache(maxsize=None)
def fibonacci_lru(n):
    if n < 2:
        return n
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)

def fibonacci_splay(n, tree):
    val = tree.find(n)
    if val is not None:
        return val

    if n < 2:
        val = n
    else:
        val = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)

    tree.insert(n, val)
    return val

##################################################
# 3. Запуск: для n=0..950, без обнулення
#    + повторення 1000 разів для кожного n
##################################################

if __name__ == "__main__":
    sys.setrecursionlimit(10**7)

    # Єдине дерево
    splay_tree = SplayTree()

    fib_indices = range(0, 951, 50)
    lru_times = []
    splay_times = []

    # Щоб «розігріти» кеш/дерево, можемо один раз викликати
    # велике n на старті (необов'язково, але іноді допомагає).
    # fibonacci_lru(950)
    # fibonacci_splay(950, splay_tree)

    for n in fib_indices:
        # LRU Cache: 1000 викликів підряд
        start = time.perf_counter()
        for _ in range(1000):
            fibonacci_lru(n)
        end = time.perf_counter()
        avg_time_lru = (end - start) / 1000.0  # середній час на один виклик
        lru_times.append(avg_time_lru)

        # Splay Tree: 1000 викликів підряд
        start = time.perf_counter()
        for _ in range(1000):
            fibonacci_splay(n, splay_tree)
        end = time.perf_counter()
        avg_time_splay = (end - start) / 1000.0
        splay_times.append(avg_time_splay)

    # Виводимо таблицю
    print("n         LRU Cache Time (s)   Splay Tree Time (s)")
    print("--------------------------------------------------")
    for i, n in enumerate(fib_indices):
        print(f"{n:<10}{lru_times[i]:<22.8f}{splay_times[i]:.8f}")

    # Побудова графіка
    plt.figure(figsize=(8, 5))
    plt.plot(list(fib_indices), lru_times, marker='o', label='LRU Cache')
    plt.plot(list(fib_indices), splay_times, marker='o', label='Splay Tree')

    plt.title("Порівняння часу (без обнулення), 1000 повторень для кожного n")
    plt.xlabel("n (індекс числа Фібоначчі)")
    plt.ylabel("Середній час виконання (секунди)")

    plt.grid(True)
    plt.legend()
    plt.show()
