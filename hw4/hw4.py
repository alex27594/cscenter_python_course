import gzip
import bz2
import io
import random

def capwords(string, sep):
    title_words = [word.title() for word in string.split(sep)]
    out_string = sep.join(title_words)
    return out_string


def cut_suffix(string, suffix):
    return string.partition(suffix)[0] + string.partition(suffix)[2]


def boxed(string, fill, pad):
    len_of_str = len(string) + 2 * pad
    out_string = "".center(len_of_str, fill) +\
                "\n" + string.center(len_of_str, fill) +\
                "\n" + "".center(len_of_str, fill)
    return out_string


def find_all(string, substring):
    places = []
    glob_place = -1
    while True:
        local_place = string[glob_place + 1:].find(substring)
        glob_place = glob_place + 1 + local_place
        if local_place == -1:
            break
        places.append(glob_place)
    return places


def common_prefix(*args):
    words = list(args)
    words.sort(key=lambda x: len(x))
    pref_word = words[0]
    for i in range(len(pref_word), 0, -1):
        pref = pref_word[:i]
        is_com_pref = True
        for word in words[1:]:
            if not word.startswith(pref):
                is_com_pref = False
        if is_com_pref:
            return pref
    return ""


def reader(path, mode="r", encoding=None):
    if path.endswith(".gz"):
        return gzip.open(path, mode=mode, encoding=encoding)
    elif path.endswith(".bz2"):
        return bz2.open(path, mode=mode, encoding=encoding)
    else:
        return open(path, mode=mode, encoding=encoding)


def parse_shebang(path):
    handle = open(path)
    first_str = handle.readline()
    return first_str[first_str.find("#!") + 2:].strip(" \n")


def words(handle):
    string = handle.read()
    return string.split(" ")


def transition_matrix(language):
    bigram_dict = {}
    for i in range(len(language) - 2):
        if (language[i], language[i + 1]) not in bigram_dict.keys():
            bigram_dict[(language[i], language[i + 1])] = [language[i + 2]]
        else:
            bigram_dict[(language[i], language[i + 1])] += [language[i + 2]]
    return bigram_dict


def markov_chain(words, transition_matrix, n):
    sentence_list = [random.choice(words), random.choice(words)]
    i = 2
    while i < n:
        if (sentence_list[i - 2], sentence_list[i - 1]) in transition_matrix.keys():
            sentence_list.append(random.choice(transition_matrix[(sentence_list[i - 2], sentence_list[i - 1])]))
        else:
            sentence_list.append(random.choice(words))
        i += 1
    return " ".join(sentence_list)


def snoop_says(path, n):
    language = words(open(path))
    m = transition_matrix(language)
    return markov_chain(language, m, 100)


"""print(1, capwords("gbjw,,,fq", ","))
print(2, cut_suffix("barfoo", "bar"))
print(boxed("Hello world", fill="*", pad=5))
print(find_all("abracadabra", "a"))
print(common_prefix("abra", "abracadabra", "abrusive"))
print(common_prefix("abra", "foobar"))
print(common_prefix("abra", "af"))
print(reader("files/example.txt"))
print(reader("files/example.txt.gz", mode="rt", encoding="ascii"))
print(reader("files/example.txt.bz2", mode="wb"))
print(parse_shebang("files/example1.txt"))
print(parse_shebang("files/example2.txt"))"""

print(snoop_says("files/snoop279.txt", 100))
