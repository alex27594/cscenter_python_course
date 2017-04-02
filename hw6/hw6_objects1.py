import functools
import math

def peel(cls):
    return set(el for el in dir(cls) if not el.startswith("_"))


class AbstractBase:
    def some_method(self):
        pass


class Base(AbstractBase):
    def some_other_method(self):
        pass


class Closeable(Base):
    def close(self):
        pass

print(peel(Closeable))


def implements(interface):
    def decorator(cls):
        @functools.wraps(cls)
        def inner(*args, **kwargs):
            assert peel(interface) == peel(cls), "method(s) " + " ".join(set.difference(peel(interface), peel(cls))) +\
                " not implemented"
            instance = cls(*args,**kwargs)
            return instance
        return inner
    return decorator


class Interface:
    def first_method(self):
        pass

    def second_method(self):
        pass

    def third_method(self):
        pass


@implements(Interface)
class ImplementingClass:
    def first_method(self):
        pass

    def second_method(self):
        pass

    def third_method(self):
        pass

ImplementingClass()


class Expr:
    def __init__(self, expr):
        self.expr = expr
        self.wrt = None

    def __cal__(self, **context):
        pass

    def d(self, wrt):
        new_expr_obj = type(self)(self.expr)
        new_expr_obj.wrt = wrt
        return new_expr_obj

    @property
    def is_constexpr(self):
        pass

    @property
    def simplified(self):
        return self

    def __neg__(self):
        return Product(Const(-1), self)

    def __pos__(self):
        return self

    def __add__(self, other):
        return Sum(self, other)

    def __sub__(self, other):
        return Sum(self, Product(Const(-1), other))

    def __mul__(self, other):
        return Product(self, other)

    def __truediv__(self, other):
        return Fraction(self, other)

    def __pow__(self, other):
        return Power(self, other)


class Const(Expr):
    def __call__(self, ** context):
        if self.wrt is None:
            return self.expr
        assert isinstance(self.wrt, Var), "not right wrt"
        return 0

    def __str__(self):
        if self.wrt is None:
            return str(self.expr)
        else:
            return "0"

    @property
    def is_constexpr(self):
        return True


class Var(Expr):
    def __call__(self, **context):
        if self.wrt is None:
            return context.get(self.expr, self.expr)
        return 1 if isinstance(self.wrt, Var) and self.wrt.expr == self.expr else 0

    def __str__(self):
        if self.wrt is None:
            return self.expr
        else:
            return "1"

    @property
    def is_constexpr(self):
        return False

print("test var and const")
print(Const(42)())
print(Const(42).d(Var("x"))())
print(Var("x")(x=42))
print(Var("x")())
print(Var("x").d(Var("x"))())
print(Var("x").d(Var("y"))())


class BinOp(Expr):
    def __init__(self, expr1, expr2):
        self.wrt = None
        self.expr1, self.expr2 = expr1, expr2

    def d(self, wrt):
        new_expr_obj = type(self)(self.expr1, self.expr2)
        new_expr_obj.wrt = wrt
        return new_expr_obj

    @property
    def is_constexpr(self):
        return self.expr1.is_constexpr and self.expr2.is_constexpr

    @property
    def simplified(self):
        if self.is_constexpr:
            self.expr1 = self.expr1.simplified
            self.expr2 = self.expr2.simplified
            return Const(type(self)(self.expr1, self.expr2)())
        else:
            self.expr1 = self.expr1.simplified
            self.expr2 = self.expr2.simplified
            return type(self)(self.expr1, self.expr2)


class Sum(BinOp):
    def __call__(self, **context):
        return self.expr1.d(self.wrt)(**context) + self.expr2.d(self.wrt)(**context)

    def __str__(self):
        if self.wrt is None:
            return "(+ {} {})".format(str(self.expr1), str(self.expr2))
        else:
            return "(+ {} {})".format(str(self.expr1.d(self.wrt)), str(self.expr2.d(self.wrt)))


class Product(BinOp):
    def __call__(self, **context):
        if self.wrt is not None:
            return self.expr1.d(self.wrt)(**context) * self.expr2(**context) +\
                self.expr2.d(self.wrt)(**context) * self.expr1(**context)
        else:
            return self.expr1(**context) * self.expr2(**context)

    def __str__(self):
        if self.wrt is None:
            return "(* {} {})".format(str(self.expr1), str(self.expr2))
        else:
            return "(+ (* {} {}) (* {} {}))".format(str(self.expr1.d(self.wrt)), str(self.expr2),
                                                    str(self.expr1), str(self.expr2.d(self.wrt)))


class Fraction(BinOp):
    def __call__(self, **context):
        if self.wrt is None:
            return (self.expr1.d(self.wrt)(**context) * self.expr2(**context) -\
                    self.expr1(**context) * self.expr2.d(self.wrt)(**context)) /\
                    self.expr2(**context) ** 2
        else:
            return self.expr1(**context)/self.expr2(**context)

    def __str__(self):
        if self.wrt is None:
            return "(/ {} {})".format(str(self.expr1), str(self.expr2))
        else:
            return "(/ (+ (* {} {}) (* -1 (* {} {}))) (** {}))".format(str(self.expr1.d(self.wrt)), str(self.expr2),
                                                                       str(self.expr1), str(self.expr2.d(self.wrt)),
                                                                       str(self.expr2))


class Power(BinOp):
    def __call__(self, **context):
        if self.wrt is not None:
            return self.expr2.expr * self.expr1(**context) ** (self.expr2.expr - 1) * self.expr1.d(self.wrt)(**context)
        else:
            return self.expr1(**context) ** self.expr2(**context)

    def __str__(self):
        if self.wrt is None:
            return "(** {} {})".format(str(self.expr1), str(self.expr2))
        else:
            return "(* (* {} (** {} {})) {})".format(str(self.expr2), str(self.expr1), str(int(str(self.expr2)) - 1),
                                                     str(self.expr1.d(self.wrt)))


def newton_raphson(expr, x0, threshold):
    x = Var("x")
    prev_x = x0
    next_x = x0 - expr(x=x0)/expr.d(x)(x=x0)
    while abs(next_x - prev_x) > threshold:
        prev_x, next_x = next_x, next_x - expr(x=next_x)/expr.d(x)(x=next_x)
    return next_x

print("test sum")
x = Var("x")
print(Sum(x, x).d(x)(x=42))
print(Sum(x, Const(2)).d(x)(x=42))
print(Sum(Const(1), Const(2)).d(x)(x=42))

print(Sum(x, x)(x=42))
print(Sum(x, Const(2))(x=42))
print(Sum(Const(1), Const(2))(x=42))

print("test product")
print(Product(x, x).d(x)(x=42))
print(Product(x, Const(2)).d(x)(x=42))
print(Product(Const(1), Const(2)).d(x)(x=42))

print(Product(x, x)(x=42))
print(Product(x, Const(2))(x=42))
print(Product(Const(1), Const(2))(x=42))

print("test fraction")
print(Fraction(x, x).d(x)(x=42))
print(Fraction(x, Const(2)).d(x)(x=42))
print(Fraction(Const(1), Const(2)).d(x)(x=42))

print(Fraction(x, x)(x=42))
print(Fraction(x, Const(2))(x=42))
print(Fraction(Const(1), Const(2))(x=42))


print("test mix sum with product")
print(Sum(x, Product(x, x)).d(x)(x=42))
print(Product(x, Sum(x, Const(2)))(x=42))

print("test mix sum with product with fraction")
print(Fraction(Product(x, Var("y")), Sum(Const(42), x)).d(x)(x=42, y=24))
print(Fraction(Product(x, Var("y")), Sum(Const(42), x)).d(Var("y"))(x=42, y=24))

print("test power")
print(Power(Fraction(Var("x"), Const(4)), Const(2))(x=42))
print(Power(Fraction(Var("x"), Const(4)), Const(2)).d(Var("x"))(x=42))

print("test str")
print(Sum(x, Product(x, x)))
print(Sum(x, Product(x, x)).d(x))
print(Product(x, Sum(x, Const(2))))
print(Power(Fraction(x, Const(4)), Const(2)))

print("operators' overriding test")
print((Const(1) - Var("x")) ** Const(3) + Var("x"))

print("test newton-raphson")
expr = (Var("x") + Const(-1)) ** Const(3) + Var("x")
zero = newton_raphson(expr, 0.5, threshold=1e-4)
print(expr)
print(zero, expr(x=zero))

print("test is_constexpr")
print((Var("x") + Const(1)).is_constexpr)
print((Const(1) + Const(42) * Var("x")).d(Var("x")).is_constexpr)
print((Const(1) + Const(42) * Const(2)).is_constexpr)

print("test simplified")
print((Const(1) + Const(42) * Const(2)).simplified)
print((Const(1) * Var("y") + Const(42) * Const(2) / Var("x")).simplified)
