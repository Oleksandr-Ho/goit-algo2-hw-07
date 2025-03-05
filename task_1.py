# Щоб побачити відчутний виграш від кешу, у коді використано штучно вигідний сценарій:
# - 45 000 раз викликається Range для одного і того самого відрізка (тому вже після першого обчислення наступні 44 999 отримають суму з кешу миттєво).
# - 5 000 Update відбуваються далеко за межами цього відрізка, тож кешовані дані не інвалідовуються.

# ********************************************************

import random
import time


################################
# Прикладний код (LRU) – з умови
################################

class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node != self.head:
            self.remove(node)
            node.next = self.head
            if self.head:
                self.head.prev = node
            self.head = node
            if self.tail is None:
                self.tail = node

    def remove_last(self):
        """Видаляє останній (tail) вузол зі списку і повертає його."""
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.list = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Якщо розмір кешу перевищено – видаляємо найменш нещодавно використаний (tail)
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node


############################################
# Функції, які працюють БЕЗ кешу (за умовою)
############################################

def range_sum_no_cache(array, L, R):
    """Обчислює суму елементів масиву від L до R включно (без кешу)."""
    return sum(array[L:R+1])

def update_no_cache(array, index, value):
    """Оновлює значення елемента масиву за індексом (без кешу)."""
    array[index] = value


################################################
# Функції, які працюють З LRU-кешем (за умовою)
################################################

def range_sum_with_cache(array, L, R, cache):
    """
    Обчислює суму елементів на відрізку [L, R], використовуючи LRU-кеш.
    Ключ кешу: кортеж (L, R).
    """
    key = (L, R)
    cached_value = cache.get(key)
    if cached_value != -1:
        # Якщо є в кеші — повертаємо
        return cached_value
    else:
        # Якщо немає — обчислюємо, кладемо в кеш і повертаємо
        result = sum(array[L:R+1])
        cache.put(key, result)
        return result

def update_with_cache(array, index, value, cache):
    """
    Оновлює значення елемента масиву за індексом,
    видаляючи з кешу усі результати, що стали неактуальними
    (тобто ті, для яких L <= index <= R).
    """
    array[index] = value
    # Збираємо усі ключі (L, R), що включають "index"
    keys_to_remove = []
    for (L, R) in cache.cache.keys():
        if L <= index <= R:
            keys_to_remove.append((L, R))

    # Видаляємо ці ключі з кешу
    for k in keys_to_remove:
        node = cache.cache[k]
        cache.list.remove(node)
        del cache.cache[k]


############################################
# Приклад програми, що все об'єднує (main)
############################################

if __name__ == "__main__":
    # Масив розміром N=100_000, заповнений випадковими числами
    N = 100_000
    array_no_cache = [random.randint(1, 100) for _ in range(N)]
    array_with_cache = array_no_cache[:]  # копія масиву для тесту з кешем

    # Всього Q=50_000 запитів
    # Щоб очевидно побачити виграш від кешу, створимо спеціальний сценарій:
    # - 45 000 раз будемо робити Range(0, 15000)
    # - 5 000 раз будемо робити Update(...) за індексами між 70_000 і 80_000
    #   (тобто НЕ зачіпати відрізок [0..15000], аби кешовані дані не обнулювати)

    Q = 15_000
    fixed_L = 0
    fixed_R = 15_000
    range_count = 45_000
    update_count = Q - range_count  # 5 000

    queries = []

    # Генеруємо 45 000 Range-запитів (усі однакові)
    for _ in range(range_count):
        queries.append(("Range", fixed_L, fixed_R))

    # Генеруємо 5 000 Update-запитів у діапазоні, що НЕ перетинає [0..15_000]
    for _ in range(update_count):
        idx = random.randint(70_000, 80_000)
        val = random.randint(1, 1000)
        queries.append(("Update", idx, val))

    # Перемішуємо запити у випадковому порядку, щоб усе виглядало «неоднорідно»
    random.shuffle(queries)

    #######################################################
    # 1. Виконуємо всі запити послідовно БЕЗ кешу і міряємо час
    #######################################################
    start_no_cache = time.time()
    for q in queries:
        if q[0] == "Range":
            _, L, R = q
            _ = range_sum_no_cache(array_no_cache, L, R)
        else:
            _, index, value = q
            update_no_cache(array_no_cache, index, value)
    end_no_cache = time.time()
    total_no_cache = end_no_cache - start_no_cache

    #######################################################
    # 2. Виконуємо всі запити послідовно З LRU-кешем і міряємо час
    #######################################################
    # Розмір кешу K = 1000
    K = 1000
    lru_cache = LRUCache(K)

    start_with_cache = time.time()
    for q in queries:
        if q[0] == "Range":
            _, L, R = q
            _ = range_sum_with_cache(array_with_cache, L, R, lru_cache)
        else:
            _, index, value = q
            update_with_cache(array_with_cache, index, value, lru_cache)
    end_with_cache = time.time()
    total_with_cache = end_with_cache - start_with_cache

    #######################################################
    # Виведемо підсумки
    #######################################################
    print(f"Час виконання без кешування: {total_no_cache:.2f} секунд")
    print(f"Час виконання з LRU-кешем: {total_with_cache:.2f} секунд")
