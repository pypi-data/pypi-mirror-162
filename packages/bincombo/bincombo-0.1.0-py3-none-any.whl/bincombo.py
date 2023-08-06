"""
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
"""

import functools
import itertools
import operator


__version__ = "0.1.0"
__all__ = (
    "AndComboMixin",
    "AndSupportMixin",
    "Combo",
    "Config",
    "OrComboMixin",
    "OrSupportMixin",
    "InvertSupportMixin",
    "combinable",
    "combine_members",
)


class Config:
    """
    Stores all types related to a type's binary combining ability.

    A ``Config`` instance has to be attached as ``BIN_CONFIG`` class attribute
    to ``base_type``, so that both ``discrete_type`` and ``combo_type`` inherit it.

    It needs to be initialized with the following parameters:

    * ``base_type``:
      A common base of ``discrete_type`` and ``combo_type``.
    * ``discrete_type``:
      The discrete type to be binary-combinable, must inherit from ``base_type``
      and at least one of ``AndSupportMixin`` and ``OrSupportMixin``.
    * ``combo_type``:
      The custom ``Combo`` subtype, must also inherit from ``base_type`` and from
      the same ``*SupportMixin``s as ``discrete_type``.
    * ``and_type``:
      A subtype of ``AndComboMixin`` and ``combo_type``.
      If ``None``, combining using the `&` operator won't be possible.
    * ``or_type``:
      A subtype of ``OrComboMixin`` and ``combo_type``.
      If ``None``, combining using the `|` operator won't be possible.

    At least one of ``and_type`` and ``or_type`` needs to be provided, otherwise a
    ``ValueError`` is raised.

    In case one of the parameters does not fulfill its constraints, a ``TypeError``
    is raised.
    """

    __slots__ = ("base_type", "discrete_type", "combo_type", "and_type", "or_type")

    def __init__(
        self, base_type, discrete_type, combo_type, and_type=None, or_type=None
    ):
        if not and_type and not or_type:
            raise ValueError("at least one of and_type and or_type is required")

        if not isinstance(base_type, type):
            raise TypeError("base_type is not a 'type'")

        if not isinstance(discrete_type, type) or not issubclass(
            discrete_type, base_type
        ):
            raise TypeError(
                "discrete_type must be a subclass of {!r}".format(base_type)
            )

        if not isinstance(combo_type, type) or not issubclass(combo_type, Combo):
            raise TypeError("combo_type must be a subclass of 'Combo'")
        if not issubclass(combo_type, base_type):
            raise TypeError("combo_type must be a subclass of {!r}".format(base_type))

        mixins = {AndSupportMixin, OrSupportMixin, InvertSupportMixin}
        discrete_mixins = set(discrete_type.__mro__).intersection(mixins)
        if not discrete_mixins.difference({InvertSupportMixin}):
            raise TypeError("discrete_type has none of {!r} as base".format(mixins))
        combo_mixins = set(combo_type.__mro__).intersection(mixins)
        if not combo_mixins.difference({InvertSupportMixin}):
            raise TypeError("combo_type has none of {!r} as base".format(mixins))
        if discrete_mixins != combo_mixins:
            raise TypeError(
                "feature of discrete_type {!r} differ from those of combo_type {!r}".format(
                    discrete_mixins, combo_mixins
                )
            )

        if and_type is not None and not issubclass(combo_type, AndSupportMixin):
            raise TypeError("combo_type must inherit from 'AndSupportMixin'")
        if or_type is not None and not issubclass(combo_type, OrSupportMixin):
            raise TypeError("combo_type must inherit from 'OrSupportMixin'")

        if and_type is not None and (
            not isinstance(and_type, type)
            or not issubclass(and_type, AndComboMixin)
            or not issubclass(and_type, combo_type)
        ):
            raise TypeError(
                "and_type must either be None or a subclass of both "
                "'AndComboMixin' and {!r}".format(combo_type)
            )
        if or_type is not None and (
            not isinstance(or_type, type)
            or not issubclass(or_type, OrComboMixin)
            or not issubclass(or_type, combo_type)
        ):
            raise TypeError(
                "or_type must either be None or a subclass of both "
                "'OrComboMixin' and {!r}".format(combo_type)
            )

        self.base_type = base_type
        self.discrete_type = discrete_type
        self.combo_type = combo_type
        self.and_type = and_type
        self.or_type = or_type


class _CommonSupportMixin:
    """
    Provides a helper method for combining objects.
    """

    __slots__ = ()

    def _bin_combine(self, other, combo_type):
        bc = self.BIN_CONFIG
        if not isinstance(other, (bc.discrete_type, bc.combo_type)):
            return NotImplemented
        left = (
            self._members
            if (
                isinstance(self, combo_type)
                or isinstance(self, bc.combo_type)
                and len(self._members) == 1
            )
            and not self._inverted
            else (self,)
        )
        right = (
            other._members
            if (
                isinstance(other, combo_type)
                or isinstance(other, bc.combo_type)
                and len(other._members) == 1
            )
            and not other._inverted
            else (other,)
        )
        return combo_type(*left, *right)


class AndSupportMixin(_CommonSupportMixin):
    """
    Adds `&` combination support to a discrete type or ``Combination`` subtype.
    """

    __slots__ = ()

    def __and__(self, other):
        return self._bin_combine(other, self.BIN_CONFIG.and_type)


class OrSupportMixin(_CommonSupportMixin):
    """
    Adds `|` combination support to a discrete type or ``Combination`` subtype.
    """

    __slots__ = ()

    def __or__(self, other):
        return self._bin_combine(other, self.BIN_CONFIG.or_type)


class InvertSupportMixin:
    """
    Adds `~` inversion support to a discrete type or ``Combination`` subtype.
    """

    __slots__ = ()

    def __invert__(self):
        bc = self.BIN_CONFIG
        if isinstance(self, bc.combo_type):
            if self._inverted and len(self._members) == 1:
                return self._members[0]
            return type(self)(*self._members, inverted=not self._inverted)
        _type = bc.or_type if bc.and_type is None else bc.and_type
        return _type(self, inverted=True)


class Combo:
    """
    Base class for the type representing a binary combination of objects of the
    discrete type (and other combinations thereof).

    It also provides a ``repr()`` reflecting the relation type and inversion state.

    Objects are meant to be immutable once initialized, so rather create a fresh
    object instead of programmatically changing non-public attributes.
    ``Combo`` is then fully thread-safe as well.

    ``TypeError`` is raised when trying to initialize with an unsupported member type.
    """

    __slots__ = ("_members", "_inverted")

    _BIN_OP_REPR = "?"

    def __init__(self, *members, inverted=False):
        bc = self.BIN_CONFIG
        for member in members:
            if not isinstance(member, (bc.discrete_type, bc.combo_type)):
                raise TypeError("unsupported member type {!r}".format(type(member)))
        self._members = members
        self._inverted = inverted

    def __repr__(self):
        if self._members:
            inner = " {} ".format(self._BIN_OP_REPR).join(map(repr, self._members))
            # Don't show parentheses for negations of a single member
            if self._inverted and len(self._members) == 1:
                return "~{}".format(inner)
        else:
            inner = self._BIN_OP_REPR
        return "{}({})".format("~" if self._inverted else "", inner)

    @property
    def inverted(self):
        """ "Whether the combination was inverted using the `~` unary operator."""
        return self._inverted

    @property
    def members(self):
        """ "Tuple of members of the combination."""
        return self._members


class AndComboMixin:
    """
    Mixin for the subtype of ``Combo`` that represents the AND relation.
    """

    __slots__ = ()

    _BIN_OP_REPR = "&"


class OrComboMixin:
    """
    Mixin for the subtype of ``Combo`` that represents the OR relation.
    """

    __slots__ = ()

    _BIN_OP_REPR = "|"


def _reformat_qualname(format_string, name):
    spl = name.rsplit(".", 1)
    name = spl[-1]
    cap_name = name[0].upper() + name[1:]
    return ".".join((*spl[:-1], format_string.format(name=name, cap_name=cap_name)))


def combinable(
    original_type=None,
    *,
    methods=(),
    properties=(),
    support_and=True,
    support_or=True,
    support_invert=True,
    base_name="Base{cap_name}",
    discrete_name="Discrete{cap_name}",
    combo_name="{cap_name}Combo",
    and_name="All{cap_name}s",
    or_name="Any{cap_name}",
):
    """
    Class decorator for making a type binary-combinable.

    It does not alter the original type, instead it creates a binary-combinable
    subtype (plus some auxiliary types) and returns it.
    This decorator is a shorthand that should be sufficient for most use cases.
    The general process of making a type binary-combinable using ``bincombo`` is
    shown in the module's docstring.

    Parameters:

    * ``original_type``:
      The type to be made binary-combinable.
      Does not need to be given explicitly if used as class decorator.
    * ``methods``:
      Tuple of method names of the discrete type which should also be available on
      combinations thereof.
      The ``combine_members()`` helper is utilized to combine boolean method call
      results of the individual combination members according to the type of relation
      (& or |).
      If, instead of just method names, two-tuples ``(name, meth)`` are given, ``meth``
      is directly used as the method implementation on the created ``Combo``
      subtype.
      This allows to call ``combine_members()`` with custom map/reduce configurations
      for combining non-boolean results, or to implement a completely different
      scheme of member aggregation.
    * ``properties``:
      Like ``methods``, except that plain attribute lookups are performed on the
      members instead of method calls.
      Also, in case of two-tuples, the function will be wrapped using ``property()``,
      so don't do that yourself.
    * ``support_and``:
      Whether objects should support combination using the `&` operator.
    * ``support_or``:
      Whether objects should support combination using the `|` operator.
    * ``support_invert``:
      Whether objects should support logical negation using the `~` unary operator.
    * ``base_name``:
      ``str.format()``-style pattern for the base type's ``__name__``.
      The placeholder `{name}` inserts the original type's ``__name__``, `{cap_name}`
      is the same with capital first letter.
    * ``discrete_name``:
      ``str.format()``-style pattern for the discrete type's ``__name__``.
      Placeholders are the same as for ``base_name``.
    * ``combo_name``:
      ``str.format()``-style pattern for the ``Combo`` subtype's ``__name__``.
      Placeholders are the same as for ``base_name``.
    * ``and_name``:
      ``str.format()``-style pattern for the AND type's ``__name__``.
      Placeholders are the same as for ``base_name``.
    * ``or_name``:
      ``str.format()``-style pattern for the AND type's ``__name__``.
      Placeholders are the same as for ``base_name``.

    At least one of ``support_and`` and ``support_or`` needs to be ``True``, a
    ``ValueError`` is raised otherwise.
    """

    if original_type is None:
        return functools.partial(
            combinable,
            methods=methods,
            properties=properties,
            support_and=support_and,
            support_or=support_or,
            support_invert=support_invert,
            base_name=base_name,
            discrete_name=discrete_name,
            combo_name=combo_name,
            and_name=and_name,
            or_name=or_name,
        )

    def _get_method_proxy(method_name):
        return lambda self, member, *a, **kw: getattr(member, method_name)(*a, **kw)

    def _get_property_proxy(property_name):
        return lambda self, member: getattr(member, property_name)

    def _get_unimplemented_method():
        def _unimplemented(self, *args, **kwargs):
            raise NotImplementedError

        return _unimplemented

    base_dict = {}
    combo_dict = {}

    for definition, is_property in itertools.chain(
        zip(methods, itertools.repeat(False)), zip(properties, itertools.repeat(True))
    ):
        if isinstance(definition, tuple):
            name, meth = definition
        elif isinstance(definition, str):
            name = definition
            meth = combine_members(
                (_get_property_proxy if is_property else _get_method_proxy)(name)
            )
        else:
            raise TypeError(
                "method/property definition must be 'str' or ('str', 'function'), "
                "not {!r}".format(definition)
            )

        unimpl = _get_unimplemented_method()
        unimpl.__module__ = original_type.__module__
        unimpl.__name__ = name
        unimpl.__qualname__ = "{}Base.{}".format(original_type.__qualname__, name)
        unimpl.__doc__ = "Stub method that raises ``NotImplementedError``."
        base_dict[name] = property(unimpl) if is_property else unimpl

        try:
            orig_meth = getattr(original_type, name)
        except AttributeError:
            meth.__module__ = original_type.__module__
            meth.__name__ = name
        else:
            functools.update_wrapper(meth, orig_meth)
        meth.__qualname__ = "{}Combo.{}".format(original_type.__qualname__, name)
        combo_dict[name] = property(meth) if is_property else meth

    mixins = []
    if support_and:
        mixins.append(AndSupportMixin)
    if support_or:
        mixins.append(OrSupportMixin)
    if support_invert:
        mixins.append(InvertSupportMixin)

    base_type = type(
        _reformat_qualname(base_name, original_type.__qualname__),
        (),
        {
            **base_dict,
            "__doc__": (
                "Common parent class of discrete {name} and {name}Combo objects, "
                "which represent a binary combination thereof.".format(
                    name=original_type.__qualname__
                )
            ),
            "__slots__": (),
        },
    )
    base_type.__module__ = original_type.__module__

    discrete_type = type(
        _reformat_qualname(discrete_name, original_type.__qualname__),
        (*mixins, original_type, base_type),
        {"__slots__": ()},
    )
    discrete_type.__module__ = original_type.__module__

    combo_type = type(
        _reformat_qualname(combo_name, original_type.__qualname__),
        (*mixins, Combo, base_type),
        {**combo_dict, "__slots__": ()},
    )
    combo_type.__module__ = original_type.__module__

    and_type = None
    if support_and:
        and_type = type(
            _reformat_qualname(and_name, original_type.__qualname__),
            (AndComboMixin, combo_type),
            {"__slots__": ()},
        )
        and_type.__module__ = original_type.__module__

    or_type = None
    if support_or:
        or_type = type(
            _reformat_qualname(or_name, original_type.__qualname__),
            (OrComboMixin, combo_type),
            {"__slots__": ()},
        )
        or_type.__module__ = original_type.__module__

    base_type.BIN_CONFIG = Config(
        base_type, discrete_type, combo_type, and_type, or_type
    )

    return discrete_type


def combine_members(
    meth=None,
    *,
    and_=(True, operator.and_, operator.not_),
    or_=(False, operator.or_, bool),
    invert=operator.not_,
):
    """
    Decorator for methods of ``Combo`` subclasses that combines members in a
    map-and-reduce fashion.

    The decorated method is called iteratively for each member of the combination,
    passing the member as first argument, followed by the original positional and
    keyword arguments, so that it can work out and return the member's result,
    e.g. by proxying the method call.

    The decorator then combines results using AND/OR operations, depending on the
    combination's type, and possibly inverts the result.
    These operations are configurable via parameters, the defaults are suitable for
    combining boolean values and behave like the ``all()`` and ``any()`` builtins.
    For instance, with default operations in the AND-case, a call is equivalent to::

        all(meth(self, member, *args, **kwargs) for member in self.members)

    Parameters:

    * ``meth``:
      The method which maps members to member results as described above.
      Does not need to be given explicitly if used as decorator.
    * ``and_``:
      A three-tuple that configures how to combine member results in the AND case:
      * initial value: this is also returned for empty combinations
      * combine operator: this is called for each member with two arguments: the
        current value and the member's result, its return becomes the current value
      * stop condition: this is called before processing the next member with the
        current value as argument, if it returns something that evaluates to ``True``,
        no more members are processed
    * ``or_``:
      A three-tuple that configures how to combine member results in the OR case:
      See ``and_`` for descriptions of the tuple elements.
    * ``invert``:
      In case the combination is a negated one, this callable is called with the
      final result and has to return the inverse value.
    """

    if meth is None:
        return functools.partial(combine_members, and_=and_, or_=or_, invert=invert)

    @functools.wraps(meth)
    def _combine_members(self, *args, **kwargs):
        bc = self.BIN_CONFIG
        if bc.and_type is not None and isinstance(self, bc.and_type):
            result, op, stop = and_
        elif bc.or_type is not None and isinstance(self, bc.or_type):
            result, op, stop = or_
        else:
            raise RuntimeError(
                "{!r} is neither the AND nor OR combo type".format(type(self))
            )
        for member in self._members:
            if stop(result):
                break
            member_result = meth(self, member, *args, **kwargs)
            result = op(result, member_result)
        return invert(result) if self._inverted else result

    return _combine_members
