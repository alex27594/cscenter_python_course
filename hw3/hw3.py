import functools


def union(*args):
    return functools.reduce(lambda acc, x: acc | x, args)


def digits(number):
    return functools.reduce(lambda acc, x: acc + [int(x)], str(number),[])


# lcm is missed


def compose(*args):
    def inner(x):
        return functools.reduce(lambda acc, func: func(acc), reversed(args), x)
    return inner


def once(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not inner.called:
            inner.called = True
            inner.cache = func(*args, **kwargs)
            return inner.cache
        else:
            return inner.cache
    inner.called = False
    return inner


def trace_if(pred):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if pred(*args, **kwargs):
                print(func.__name__, args, kwargs)
            return func(*args, **kwargs)
        return inner
    return decorator


@trace_if(lambda x, y, **kwargs: kwargs.get("integral"))
def div(x, y, integral=False):
    return x // y if integral else x / y


def n_times(n):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for i in range(0, n):
                func(*args, **kwargs)
        return inner
    return decorator


@n_times(3)
def do_something():
    print("Something is going on!")


def project():
    def decorator(func=None, *, depends_on=[]):
        if func is None:
            return lambda func: decorator(func, depends_on=depends_on)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            for dependency in inner.dependencies:
                if dependency not in decorator.runned_tasks:
                    dep_func = [f for f in decorator.tasks if f.__name__ == dependency][0]
                    dep_func()
                    decorator.runned_tasks.append(dependency)
            decorator.runned_tasks.append(func.__name__)
            return func(*args, **kwargs)
        inner.dependencies = [depends_on] if type(depends_on) != list else depends_on
        inner.get_dependencies = lambda: inner.dependencies
        decorator.tasks += [func]
        return inner
    decorator.get_all = lambda: [x.__name__ for x in decorator.tasks]
    decorator.runned_tasks = []
    decorator.tasks = []
    return decorator




