bincombo
========

Make any type binary-combinable with a single line of code.

The most obvious use case arguably is the creation of binary expressions over custom
types, but ``bincombo`` is not limited to combination of boolean values.
By providing appropriate map/reduce operations, any type of data of the discrete
members of a combination can be aggregated to form a combined result.

The implementation solely relies on inheritance, no meta programming is involved.
You are free to use your own metaclasses, should you wish to do so.

Suppose you have a custom type ``Check``, which accepts or rejects values depending
on the result of the invocation of some callable.
You can make instances of it combinable using the binary operators `&` (and) and `|`
(or) and also support the unary `~` (invert) by using the ``combinable()`` decorator::

    import bincombo

    @bincombo.combinable(methods=("check",))
    class Check:
        __slots__ = ("checker",)

        def __init__(self, checker):
            self.checker = checker

        def check(self, value):
            return self.checker(value)

Now, ``Check`` objects can be binary-combined::

    c1 = Check(lambda v: isinstance(v, int) and v >= 42)
    c2 = Check(lambda v: isinstance(v, str))
    c3 = Check(lambda v: "hello" in v)
    c = c1 | c2 & ~c3
    c.check(41)  # False
    c.check(42)  # True
    c.check("hello, world!")  # False
    c.check("hey, world!")  # True

The ``combinable()`` decorator creates a number of types needed to represent discrete
checks and combinations thereof.
These are stored in a ``Config`` object, which is aavailable as class attribute
``BIN_CONFIG`` of ``Check``.
It can be worth storing these types as module attributes alongside your ``Check``
class to have them at hand for explicit use or type checking::

    BaseCheck = Check.BIN_CONFIG.base_type
    CheckCombo = Check.BIN_CONFIG.combo_type
    AllChecks = Check.BIN_CONFIG.and_type
    AnyCheck = Check.BIN_CONFIG.or_type

All types in this module have ``__slots__`` defined for smaller memory footprints
and improved lookup times, as have the types created by ``combinable()``.
It is recommended to also equip your own type with ``__slots__`` if possible to
benefit from entirely ``__dict__``-less objects.

To gain a better understanding of how all the types relate or to further customize
them, here is how you would make ``Check`` binary-combinable without using the
``combinable()`` helper::

    # This is a base class from which both the discrete Check type and the type
    # representing a combination of Check objects will inherit.
    # It can be used, for instance, to test whether some object is Check-like
    # using isinstance(obj, BaseCheck).
    class BaseCheck:
        __slots__ = ()

    # Check should support all three operations.
    feature_mixins = (
        bincombo.AndSupportMixin, bincombo.OrSupportMixin, bincombo.InvertSupportMixin
    )

    # This is the type that would normally be returned by combinable() decorator.
    # Here it replaces the original Check, but you could also give it a different name.
    class Check(*feature_mixins, Check, BaseCheck):
        __slots__ = ()

    # Objects of this type represent (possibly negated) AND/OR combinations of
    # Check objects.
    class CheckCombo(*feature_mixins, bincombo.Combo, BaseCheck):
        __slots__ = ()

        # Create a proxy check() method that queries an individual combo member.
        # bincombo will call this method for all members, combining the returned
        # boolean values using and/or, depending on the combination type, and possibly
        # invert the final result.
        @bincombo.combine_members
        def check(self, member, value):
            return member.check(value)

    # This is an AND combination.
    class AllChecks(bincombo.AndComboMixin, CheckCombo):
        __slots__ = ()

    # This is an OR combination.
    class AnyCheck(bincombo.OrComboMixin, CheckCombo):
        __slots__ = ()

    # Finally, bincombo has to be taught all the types just created.
    # By attaching the Config object to BaseCheck as a class attribute, both Check
    # and CheckCombo instances will have it available due to inheritance.
    BaseCheck.BIN_CONFIG = bincombo.Config(
        BaseCheck, Check, CheckCombo, AllChecks, AnyCheck
    )

Further customization of the combining abilities is possible, the documentations of
``combinable()``, ``combine_members()`` and ``Config`` have more information.
