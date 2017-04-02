def compose(f1, f2):
    def inner(x):
        return f1(f2(x))
    return inner


def constantly(c):
    def inner():
        return c
    return inner


def flip(func):
    def inner(*args):
        args = list(reversed(args))
        return func(*args)
    return inner


def curry(func, *args):
    def inner(*args1):
        return func(*(list(args) + list(args1)))
    return inner


def enumerate(seq, start=None):
    start = start or 0
    return zip(seq, range(start, len(seq) + start))


def which(pred, seq):
    return (i for i in range(len(seq)) if pred(seq[i]))


def all(pred, seq):
    if len(list(filter(pred, seq))) == len(seq):
        return True
    else:
        return False


def any(pred, seq):
    if len([x for x in seq if pred(x)]) > 0:
        return True
    else:
        return False


def any_of(str):
    def inner(input):
        if not input:
            return "ERROR", "eof", input
        elif input[0] not in str:
            return "ERROR", "expected some of this " + str + " got " + input[0],input
        else:
            return "OK", input[0], input[1:]
    return inner


def char(ch):
    def inner(input):
        if not input:
            return "ERROR", "eof", input
        elif input[0] != ch:
            return "ERROR", "expected " + ch + " got " + input[0], input
        else:
            return "OK", input[0], input[1:]
    return inner


def chain(*args):
    def inner(input):
        result = []
        leftover = input
        for f in args:
            tag, res, leftover = f(leftover)
            if tag == "ERROR":
                return tag, res, leftover
            result += res
        return "OK", result, leftover
    return inner


def choice(*args):
    def inner(input):
        for f in args:
            tag, result, leftover = f(input)
            if tag == "OK":
                return tag, result,leftover
        return "ERROR", "none matched", input
    return inner


def many(parser, empty=True):
    def inner(input):
        result = []
        leftover = input
        first = True
        while True:
            tag, res, leftover = parser(leftover)
            if tag != "OK":
                if first:
                    if empty:
                        return "OK", [], input
                    else:
                        return tag, res, leftover
                else:
                    return "OK", result, leftover
            result += res
            if first:
                first = False
        return "OK", result, leftover
    return inner


def skip(parser):
    def inner(input):
        tag, result, leftover = parser(input)
        if tag == "OK":
            result = None
            return tag, result, leftover
        else:
            return tag, result, leftover
    return inner


def sep_by(p, separator):
    def inner(input):
        tag, result1, leftover = p(input)
        if tag == "OK":
            chain_parser = chain(separator, p)
            many_parser = many(chain_parser)
            tag, result2, leftover = many_parser(leftover)
            return tag, [result1] + result2, leftover
        return tag, result1, leftover
    return inner


def parse(parser, input):
    tag, result, leftover = parser(input)
    assert tag == "OK", (result, leftover)
    return result


p = sep_by(any_of("1234567890"), char(","))
print(parse(p, "1,2,3"))
#print(parse(p, "..."))




