from collections import namedtuple
from collections import OrderedDict
from collections import Counter
from collections import defaultdict
import functools

Factor = namedtuple("Factor", ["elments", "levels"])


def factor(input_list):
    seen = set()
    ordict = OrderedDict()
    c = 0
    for i in range(len(input_list)):
        if input_list[i] not in seen:
            seen.add(input_list[i])
            ordict[input_list[i]] = c
            c += 1
    return Factor([ordict[el] for el in input_list], ordict)

# print(factor(["a", "a", "b"]))
# print(factor(["a", "b", "c", "b", "a"]))


def lru_cache(func=None, *, maxsize=64):
    if func is None:
        return lambda func: lru_cache(func, maxsize=maxsize)
    CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "cursize"])

    @functools.wraps(func)
    def inner(*args, **kwargs):
        if str(args) + str(kwargs) in inner.cache:
            inner.hits += 1
            return inner.cache[str(args) + str(kwargs)]
        else:
            inner.misses += 1
            res = func(*args, **kwargs)
            inner.cache[str(args) + str(kwargs)] = res
            if len(inner.cache) > maxsize:
                inner.cache.popitem(last=False)
            return res

    def cache_info():
        return CacheInfo(inner.hits, inner.misses, maxsize, len(inner.cache))

    def cache_clear():
        inner.cache.clear()
        inner.misses = 0
        inner.hits = 0
    inner.cache_info = cache_info
    inner.cache_clear = cache_clear
    inner.cache = OrderedDict()
    inner.misses = 0
    inner.hits = 0
    return inner


@lru_cache(maxsize=4)
def fib(n):
    return n if n <= 1 else fib(n - 1) + fib(n - 2)
"""
print(fib(3))
print(fib(2))
print(fib(4))
print(fib(5))
print(fib.cache_info())
print(fib(7))
print(fib.cache_info())
print(fib(4))
print(fib.cache_info())
fib.cache_clear()
print(fib.cache_info())
"""

def group_by(input_list, func):
    output_dict = defaultdict(list)
    for el in input_list:
        output_dict[func(el)].append(el)
    return dict(output_dict)

# print(group_by(["foo", "boo", "barbra"], len))


def invert(input_dict):
    output_dict = defaultdict(set)
    for item in input_dict.items():
        output_dict[item[1]].add(item[0])
    return dict(output_dict)

# print(invert({"a": 42, "b": 42, "c": 24}))


def export_graph(g, labels, path):
    seen_edges = set()
    handle = open(path, "w")
    handle.write("graph {\n")
    for key in g.keys():
        handle.write("{} [label='{}']\n".format(key, labels[key]))
        for j in range(len(g[key])):
            if str(key) + "--" + str(g[key][j]) not in seen_edges:
                handle.write("{} -- {}\n".format(key, g[key][j]))
                seen_edges.add(str(key) + "--" + str(g[key][j]))
                seen_edges.add(str(g[key][j]) + "--" + str(key))
    handle.write("}")
"""
labels = ["a", "b", "c"]
g = {0: [1, 2], 1: [0], 2: [0]}
export_graph(g, labels, "files/graph.dot")
"""

def hamming_distance(word, other_word):
    """
    for the case of equal lengths
    :param word:
    :param other_word:
    :return: dist
    """
    dist = 0
    if len(word) != len(other_word):
        dist += abs(len(word) - len(other_word))
    for i in range(min(len(word), len(other_word))):
        if word[i] != other_word[i]:
            dist += 1
    return dist


def build_graph(words, mismatch_percent):
    seen_edges = set()
    graph = defaultdict(list)
    for i in range(len(words)):
        have_neighbours = 0
        for j in range(len(words)):
            if i != j and len(words[i]) == len(words[j]) and \
                            hamming_distance(words[i], words[j]) <= mismatch_percent * len(words) / 100:
                have_neighbours += 1
                if str(i) + "-" + str(j) not in seen_edges:
                    graph[i].append(j)
                    graph[j].append(i)
                    seen_edges.add(str(i) + "-" + str(j))
                    seen_edges.add(str(j) + "-" + str(i))
        if have_neighbours == 0:
            graph[i] = []
    return dict(graph)


def find_connected_components(graph):
    connected_components = []
    unseen_vertices = list(graph.keys())
    must_to_see_vertices = []
    while len(unseen_vertices) > 0:
        must_to_see_vertices.append(unseen_vertices[0])
        comp = []
        while len(must_to_see_vertices) > 0:
            v = must_to_see_vertices.pop()
            comp.append(v)
            unseen_vertices.remove(v)
            for o_v in graph[v]:
                if o_v in unseen_vertices and o_v not in must_to_see_vertices:
                    must_to_see_vertices.append(o_v)
        connected_components.append(comp)
    return connected_components


def find_consensus(words):
    output_word = ""
    for i in range(len(words[0])):
        counter = Counter([words[j][i] for j in range(len(words))])
        ch = max(counter.items(), key=lambda item: item[1])[0]
        output_word += ch
    return output_word


def correct_typos(words, mismatch_percent):
    graph = build_graph(words, mismatch_percent)
    connected_components = find_connected_components(graph)
    for i in range(len(words)):
        for comp in connected_components:
            if i in comp:
                cur_comp = comp
        new_word = find_consensus([words[j] for j in range(len(words)) if j in cur_comp])
        words[i] = new_word
    return words


words = ["hello", "hello", "helol", "ehllo", "tiger", "tiger", "tuger", "tigel", "field", "abracadabra"]
"""g = build_graph(words, mismatch_percent=30.)
print(g)
con_comp = find_connected_components(g)
print(con_comp)
print(find_consensus(["hello", "helol", "ehllo"]))
print(find_consensus(["bug", "bow", "bag", "bar"]))"""
print(correct_typos(words, mismatch_percent=30.))