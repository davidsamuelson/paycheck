import paycheck
from paycheck.generator import PayCheckGenerator

from functools import partial
from itertools import izip, izip_longest, islice, repeat
import sys
from types import FunctionType
from generator import custom_generators, PayCheckGenerator
from new import classobj


class PaycheckTypeException(Exception):
    ''' raised when an attempt to register an extant type '''
    pass


def with_checker(*args, **keywords):
    if len(args) == 1 and isinstance(args[0],FunctionType):
        return Checker()(args[0])
    else:
        return Checker(*args, **keywords)


def register_type(name, func):
    '''
    dynamically add a new generated type

    func must be a callable which requires zero arguments
    and returns a value of the type we want.

    An error is raised if the name is already registered.
    '''
    if name in custom_generators:
        raise PaycheckTypeException('{} already registered!'.format(name))

    def __next__(self, *args, **kargs):
        ''' wrapped func as a PayCheckGenerator.__next__ method '''
        return func(*args, **kargs)
    new_class = classobj('{}_PaycheckGenerator'.format(name),
                         (PayCheckGenerator,), {'__next__': __next__})
    custom_generators[name] = new_class


class Checker(object):
    
    def __init__(self, *args, **keywords):
        self._number_of_calls = keywords.pop('number_of_calls', 100)
        self._throw_arguments_exception = keywords.pop('throw_arguments_exception', True)
        self._verbose = keywords.pop('verbose', False) 
        self._argument_generators = [PayCheckGenerator.get(t) for t in args]
        self._keyword_generators = [izip(repeat(name),PayCheckGenerator.get(t)) for (name,t) in keywords.iteritems()]
    
    def __call__(self, test_func):
        if test_func.func_defaults:
            self._argument_generators += [PayCheckGenerator.get(t) for t in test_func.func_defaults]
        if len(self._argument_generators) + len(self._keyword_generators) > 0:
            argument_generators = izip(*self._argument_generators)
            keyword_generators = izip(*self._keyword_generators)
            generator = islice(izip_longest(argument_generators,keyword_generators,fillvalue=()),self._number_of_calls)
        else:
            generator = repeat(((),()),self._number_of_calls)
        def wrapper(*pre_args):
            i = 0
            for (args,keywords) in generator:
                if self._verbose:
                    sys.stderr.write("%d: %r\n" % (i, args))
                try:
                    test_func(*(pre_args+args), **dict(keywords))
                except Exception, e:
                    if not self._throw_arguments_exception:
                        raise
                    if sys.version_info[0] < 3:
                        try:
                            new_e = e.__class__("Failed for input %s with message '%s'" % (args+keywords,e))
                        except:
                            new_e = e
                        raise new_e, None, sys.exc_traceback
                    else:
                        raise Exception("Failed for input {}".format(args))
                i += 1
        
        wrapper.__doc__ = test_func.__doc__
        wrapper.__name__ = test_func.__name__

        return wrapper

__all__ = [
    'with_checker',
    'Checker',
]
