from django_auxilium.utils.functools.cache import cache, cache_property, memoize


class Foo(object):
    def __init__(self):
        self.counter = 5

    @cache
    def foo(self):
        """hello world"""
        self.counter += 1
        return self.counter

    @memoize
    def bar(self, bar):
        """bunnies here"""
        self.counter += 1
        return self.counter

    @cache(as_property=True)
    def stuff(self):
        """bunnies here"""
        self.counter += 1
        return self.counter

    @cache_property
    def things(self):
        """bunnies here"""
        self.counter += 1
        return self.counter


f = Foo()

assert f.foo() == 6
assert f.foo() == 6
assert f.foo.pop() == 6
assert f.foo() == 7

assert f.bar('hello') == 8
assert f.bar('world') == 9
assert f.bar('hello') == 8
assert f.bar('world') == 9
assert f.bar.pop('hello') == 8
assert f.bar('hello') == 10

assert f.stuff == 11
assert f.stuff == 11
del f.stuff
assert f.stuff == 12

assert f.things == 13
assert f.things == 13
del f.things
assert f.things == 14


counter = 5


@cache
def foo():
    """stuff here"""
    global counter
    counter += 1
    return counter


@memoize
def bar(a):
    """something here"""
    global counter
    counter += 1
    return counter


# f = Foo()
# g = Foo()
# print(Foo.foo.__doc__)
# print(f.foo.__doc__)
# print(Foo.foo.__module__)
# print(f.foo.__module__)
# print(Foo.foo, type(Foo.foo))
# print(f.foo)
# print(f.foo())
# print(f.foo())
# print(f.foo.pop)
# print(f.foo.pop())
# print(f.foo())
# print(f.foo())
# print(f.foo())
# print('-----')
# print(Foo.bar.__doc__)
# print(f.bar.__doc__)
# print(Foo.bar.__module__)
# print(f.bar.__module__)
# print(f.bar)
# print(f.bar('bunnies'))
# print(f.bar('bunnies'))
# print(f.bar('rainbows'))
# print(f.bar('rainbows'))
# print(f.bar('bunnies'))
# print(f.bar.pop('rainbows'))
# print(f.bar('rainbows'))
# print(f.bar.pop('bunnies'))
# print(f.bar('bunnies'))
# print('-----------')
# print(foo)
# print(foo.__doc__)
# print(foo())
# print(foo())
# print(foo.pop())
# print(foo())
# print('-----------')
# print(bar)
# print(bar.__doc__)
# print(bar('a'))
# print(bar('a'))
# print(bar('b'))
# print(bar.pop('b'))
# print(bar.pop('a'))
# print(bar('a'))
