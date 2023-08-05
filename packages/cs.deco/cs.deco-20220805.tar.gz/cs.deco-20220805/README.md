Assorted decorator functions.

*Latest release 20220805*:
@OBSOLETE: small improvements.

## Function `cached(*args, **kwargs)`

Former name for @cachedmethod.

## Function `cachedmethod(*da, **dkw)`

Decorator to cache the result of an instance or class method
and keep a revision counter for changes.

The cached values are stored on the instance (`self`).
The revision counter supports the `@revised` decorator.

This decorator may be used in 2 modes.
Directly:

    @cachedmethod
    def method(self, ...)

or indirectly:

    @cachedmethod(poll_delay=0.25)
    def method(self, ...)

Optional keyword arguments:
* `attr_name`: the basis name for the supporting attributes.
  Default: the name of the method.
* `poll_delay`: minimum time between polls; after the first
  access, subsequent accesses before the `poll_delay` has elapsed
  will return the cached value.
  Default: `None`, meaning the value never becomes stale.
* `sig_func`: a signature function, which should be significantly
  cheaper than the method. If the signature is unchanged, the
  cached value will be returned. The signature function
  expects the instance (`self`) as its first parameter.
  Default: `None`, meaning no signature function;
  the first computed value will be kept and never updated.
* `unset_value`: the value to return before the method has been
  called successfully.
  Default: `None`.

If the method raises an exception, this will be logged and
the method will return the previously cached value,
unless there is not yet a cached value
in which case the exception will be reraised.

If the signature function raises an exception
then a log message is issued and the signature is considered unchanged.

An example use of this decorator might be to keep a "live"
configuration data structure, parsed from a configuration
file which might be modified after the program starts. One
might provide a signature function which called `os.stat()` on
the file to check for changes before invoking a full read and
parse of the file.

*Note*: use of this decorator requires the `cs.pfx` module.

## Function `contextdecorator(*da, **dkw)`

A decorator for a context manager function `cmgrfunc`
which turns it into a decorator for other functions.

This supports easy implementation of "setup" and "teardown"
code around other functions without the tedium of defining
the wrapper function itself. See the examples below.

The resulting context manager accepts an optional keyword
parameter `provide_context`, default `False`. If true, the
context returned from the context manager is provided as the
first argument to the call to the wrapped function.

Note that the context manager function `cmgrfunc`
has _not_ yet been wrapped with `@contextmanager`,
that is done by `@contextdecorator`.

This decorator supports both normal functions and generator functions.

With a normal function the process is:
* call the context manager with `(func,a,kw,*da,**dkw)`,
  returning `ctxt`,
  where `da` and `dkw` are the positional and keyword parameters
  supplied when the decorator was defined.
* within the context
  return the value of `func(ctxt,*a,**kw)` if `provide_context` is true
  or the value of `func(*a,**kw)` if not (the default)

With a generator function the process is:
* obtain an iterator by calling `func(*a,**kw)`
* for iterate over the iterator, yielding its results,
  by calling the context manager with `(func,a,kw,**da,**dkw)`,
  around each `next()`
Note that it is an error to provide a true value for `provide_context`
if the decorated function is a generator function.

Some examples follow.

Trace the call and return of a specific function:

    @contextdecorator
    def tracecall(func, a, kw):
        """ Trace the call and return from some function.
            This can easily be adapted to purposes such as timing a
            function call or logging use.
        """
        print("call %s(*%r,**%r)" % (func, a, kw))
        try:
          yield
        except Exception as e:
          print("exception from %s(*%r,**%r): %s" % (func, a, kw, e))
          raise
        else:
          print("return from %s(*%r,**%r)" % (func, a, kw))

    @tracecall
    def f():
        """ Some function to trace.
        """

    @tracecall(provide_context=True):
    def f(ctxt, *a, **kw):
        """ A function expecting the context object as its first argument,
            ahead of whatever other arguments it would normally require.
        """

See who is making use of a generator's values,
when a generator might be invoked in one place and consumed elsewhere:

    from cs.py.stack import caller

    @contextdecorator
    def genuser(genfunc, *a, **kw):
        user = caller(-4)
        print(f"iterate over {genfunc}(*{a!r},**{kw!r}) from {user}")
        yield

    @genuser
    def linesof(filename):
        with open(filename) as f:
            yield from f

    # obtain a generator of lines here
    lines = linesof(__file__)

    # perhaps much later, or in another function
    for lineno, line in enumerate(lines, 1):
        print("line %d: %d words" % (lineno, len(line.split())))

Turn on "verbose mode" around a particular function:

    import sys
    import threading
    from cs.context import stackattrs

    class State(threading.local):
        def __init__(self):
            # verbose if stderr is on a terminal
            self.verbose = sys.stderr.isatty()

    # per thread global state
    state = State()

    @contextdecorator
    def verbose(func):
        with stackattrs(state, verbose=True) as old_attrs:
            if not old_attrs['verbose']:
                print(f"enabled verbose={state.verbose} for function {func}")
            # yield the previous verbosity as the context
            yield old_attrs['verbose']

    # turn on verbose mode
    @verbose
    def func(x, y):
        if state.verbose:
            # print if verbose
            print("x =", x, "y =", y)

    # turn on verbose mode and also pass in the previous state
    # as the first argument
    @verbose(provide_context=True):
    def func2(old_verbose, x, y):
        if state.verbose:
            # print if verbose
            print("old_verbosity =", old_verbose, "x =", x, "y =", y)

## Function `contextual(func)`

Wrap a simple function as a context manager.

This was written to support users of `@strable`,
which requires its `open_func` to return a context manager;
this turns an arbitrary function into a context manager.

Example promoting a trivial function:

    >>> f = lambda: 3
    >>> cf = contextual(f)
    >>> with cf() as x: print(x)
    3

## Function `decorator(deco)`

Wrapper for decorator functions to support optional arguments.

The actual decorator function ends up being called as:

    mydeco(func, *da, **dkw)

allowing `da` and `dkw` to affect the behaviour of the decorator `mydeco`.

Examples:

    # define your decorator as if always called with func and args
    @decorator
    def mydeco(func, *da, arg2=None):
      ... decorate func subject to the values of da and arg2

    # mydeco called with defaults
    @mydeco
    def func1(...):
      ...

    @ mydeco called with nondefault arguments
    @mydeco('foo', arg2='bah')
    def func2(...):
      ...

## Function `fmtdoc(func)`

Decorator to replace a function's docstring with that string
formatted against the function's module `__dict__`.

This supports simple formatted docstrings:

    ENVVAR_NAME = 'FUNC_DEFAULT'

    @fmtdoc
    def func():
        """Do something with os.environ[{ENVVAR_NAME}]."""
        print(os.environ[ENVVAR_NAME])

This gives `func` this docstring:

    Do something with os.environ[FUNC_DEFAULT].

*Warning*: this decorator is intended for wiring "constants"
into docstrings, not for dynamic values. Use for other types
of values should be considered with trepidation.

## Function `logging_wrapper(*da, **dkw)`

Decorator for logging call shims
which bumps the `stacklevel` keyword argument so that the logging system
chooses the correct frame to cite in messages.

Note: has no effect on Python < 3.8 because `stacklevel` only
appeared in that version.

## Function `observable_class(property_names, only_unequal=False)`

Class decorator to make various instance attributes observable.

Parameters:
* `property_names`:
  an interable of instance property names to set up as
  observable properties. As a special case a single `str` can
  be supplied if only one attribute is to be observed.
* `only_unequal`:
  only call the observers if the new property value is not
  equal to the previous proerty value. This requires property
  values to be comparable for inequality.
  Default: `False`, meaning that all updates will be reported.

## Function `OBSOLETE(*da, **dkw)`

Decorator for obsolete functions.

Use:

    @OBSOLETE
    def func(...):

or

    @OBSOLETE("new_func_name")
    def func(...):

This emits a warning log message before calling the decorated function.
Only one warning is emitted per calling location.

## Function `strable(*da, **dkw)`

Decorator for functions which may accept a `str`
instead of their core type.

Parameters:
* `func`: the function to decorate
* `open_func`: the "open" factory to produce the core type
  if a string is provided;
  the default is the builtin "open" function.
  The returned value should be a context manager.
  Simpler functions can be decorated with `@contextual`
  to turn them into context managers if need be.

The usual (and default) example is a function to process an
open file, designed to be handed a file object but which may
be called with a filename. If the first argument is a `str`
then that file is opened and the function called with the
open file.

Examples:

    @strable
    def count_lines(f):
      return len(line for line in f)

    class Recording:
      "Class representing a video recording."
      ...
    @strable(open_func=Recording)
    def process_video(r):
      ... do stuff with `r` as a Recording instance ...

*Note*: use of this decorator requires the `cs.pfx` module.

# Release Log



*Release 20220805*:
@OBSOLETE: small improvements.

*Release 20220327*:
Some fixes for @cachedmethod.

*Release 20220311*:
@cachedmethod: change the meaning of poll_delay=None to mean "never goes stale" as I had thought it already did.

*Release 20220227*:
@cachedmethod: more paranoid access to the revision attribute.

*Release 20210823*:
@decorator: preserve the __name__ of the wrapped function.

*Release 20210123*:
Syntax backport for older Pythons.

*Release 20201202*:
@decorator: tweak test for callable(da[0]) to accord with the docstring.

*Release 20201025*:
New @contextdecorator decorator for context managers to turn them into setup/teardown decorators.

*Release 20201020*:
* @cachedmethod: bugfix cache logic.
* @strable: support generator functions.

*Release 20200725*:
Overdue upgrade of @decorator to support combining the function and decorator args in one call.

*Release 20200517.2*:
Minor upgrade to @OBSOLETE.

*Release 20200517.1*:
Tweak @OBSOLETE and @cached (obsolete name for @cachedmethod).

*Release 20200517*:
Get warning() from cs.gimmicks.

*Release 20200417*:
* @decorator: do not override __doc__ on the decorated function, just provide default.
* New @logging_wrapper which bumps the `stacklevel` parameter in Python 3.8 and above so that shims recite the correct caller.

*Release 20200318.1*:
New @OBSOLETE to issue a warning on a call to an obsolete function, like an improved @cs.logutils.OBSOLETE (which needs to retire).

*Release 20200318*:
@cachedmethod: tighten up the "is the value changed" try/except.

*Release 20191012*:
* New @contextual decorator to turn a simple function into a context manager.
* @strable: mention context manager requirement and @contextual as workaround.

*Release 20191006*:
Rename @cached to @cachedmethod, leave compatible @cached behind which issues a warning (will be removed in a future release).

*Release 20191004*:
Avoid circular import with cs.pfx by removing requirement and doing the import later if needed.

*Release 20190905*:
Bugfix @deco: it turns out that you may not set the .__module__ attribute on a property object.

*Release 20190830.2*:
Make some getattr calls robust.

*Release 20190830.1*:
@decorator: set the __module__ of the wrapper.

*Release 20190830*:
@decorator: set the __module__ of the wrapper from the decorated target, aids cs.distinf.

*Release 20190729*:
@cached: sidestep uninitialised value.

*Release 20190601.1*:
@strable: fix the example in the docstring.

*Release 20190601*:
* Bugfix @decorator to correctly propagate the docstring of the subdecorator.
* Improve other docstrings.

*Release 20190526*:
@decorator: add support for positional arguments and rewrite - simpler and clearer.

*Release 20190512*:
@fmtdoc: add caveat against misuse of this decorator.

*Release 20190404*:
New @fmtdoc decorator to format a function's doctsring against its module's globals.

*Release 20190403*:
* @cached: bugfix: avoid using unset sig_func value on first pass.
* @observable_class: further tweaks.

*Release 20190322.1*:
@observable_class: bugfix __init__ wrapper function.

*Release 20190322*:
* New class decorator @observable_class.
* Bugfix import of "warning".

*Release 20190309*:
@cached: improve the exception handling.

*Release 20190307.2*:
Fix docstring typo.

*Release 20190307.1*:
Bugfix @decorator: final plumbing step for decorated decorator.

*Release 20190307*:
* @decorator: drop unused arguments, they get used by the returned decorator.
* Rework the @cached logic.

*Release 20190220*:
* Bugfix @decorator decorator, do not decorate twice.
* Have a cut at inheriting the decorated function's docstring.

*Release 20181227*:
* New decoartor @strable for function which may accept a str instead of their primary type.
* Improvements to @cached.

*Release 20171231*:
Initial PyPI release.
