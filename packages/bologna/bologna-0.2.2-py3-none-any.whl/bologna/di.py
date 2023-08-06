import asyncio
import functools
import inspect

_injectables = dict()


def provide(name, value):
    _injectables[name] = value


def inject(f):
    if inspect.isawaitable(f):
        return _inject_async(f)
    else:
        return _inject_sync(f)


class InjectionError(Exception):
    pass


def providable_parameters(parameter_names):
    global _injectables
    return set(_injectables.keys() & set(parameter_names))


def _inject_sync(f):
    global _injectables
    (
        pos_only_parameters,
        pos_key_parameters,
        var_pos_key_parameters,
        key_only_parameters,
        var_key_parameters,
    ) = analyze_signature(f)

    @functools.wraps(f)
    def wrapper(*args, **kwargs):

        (
            key_only_arguments,
            pos_key_arguments,
            pos_only_arguments,
            var_key_arguments,
            var_pos_key_arguments,
        ) = construct_arguments(
            f,
            pos_only_parameters,
            pos_key_parameters,
            var_pos_key_parameters,
            key_only_parameters,
            var_key_parameters,
            args,
            kwargs,
        )

        # todo
        return f(
            *pos_only_arguments.values(),
            *pos_key_arguments.values(),
            *var_pos_key_arguments.values(),
            *key_only_arguments,
            **var_key_arguments,
        )

    return wrapper


def analyze_signature(f):
    sig = inspect.signature(f)
    pos_only_parameters = [
        name
        for name, param in sig.parameters.items()
        if param.kind == param.POSITIONAL_ONLY
    ]
    pos_key_parameters = [
        name
        for name, param in sig.parameters.items()
        if param.kind == param.POSITIONAL_OR_KEYWORD
    ]
    var_pos_key_parameters = [
        name
        for name, param in sig.parameters.items()
        if param.kind == param.VAR_POSITIONAL
    ]
    key_only_parameters = [
        name
        for name, param in sig.parameters.items()
        if param.kind == param.KEYWORD_ONLY
    ]
    var_key_parameters = [
        name
        for name, param in sig.parameters.items()
        if param.kind == param.VAR_KEYWORD
    ]

    return (
        pos_only_parameters,
        pos_key_parameters,
        var_pos_key_parameters,
        key_only_parameters,
        var_key_parameters,
    )


def construct_arguments(
    f,
    pos_only_parameters,
    pos_key_parameters,
    var_pos_key_parameters,
    key_only_parameters,
    var_key_parameters,
    args,
    kwargs,
):
    # the amount of *args provided
    #   - must always include all the positional only parameters, except those that are able to be injected
    #   - needn't include all pos_key parameters, but those that aren't must be included in either the **kwargs or
    #     must be able to be injected
    providable_positional_only_parameters = providable_parameters(pos_only_parameters)
    if len(pos_only_parameters) > len(args) + len(
        providable_positional_only_parameters
    ):
        raise InjectionError(
            f"Function {f.__name__} has {len(pos_only_parameters)} positional only parameters(s), "
            f"received only {len(args)} non-keyword argument(s), excluding parameter(s) {providable_positional_only_parameters} which can be injected."
        )
    iargs = iter(args)
    # construct all positional-only arguments. We assume that everytime a value can be injected, it is not passed manually.
    pos_only_arguments = {
        name: next(iargs)
        if name not in providable_positional_only_parameters
        else _injectables[name]
        for name in pos_only_parameters
    }
    print(pos_only_arguments)
    remaining_args = list(iargs)
    iargs = iter(remaining_args)
    # now moving on to pos-key-parameters, we
    providable_pos_key_parameters = providable_parameters(pos_key_parameters)
    if len(pos_key_parameters) > len(remaining_args) + len(
        providable_pos_key_parameters
    ):
        raise InjectionError(
            f"Function {f.__name__} has {len(pos_key_parameters)} positional or keyword parameters,"
            f"received at most {len(remaining_args)} non-keyword argument(s), excluding parameter(s) {providable_pos_key_parameters} which can be injected."
        )
    # construct all positional-or-keyword arguments. We assume that everytime a value can be injected, it is not passed manually.
    pos_key_arguments = {
        name: next(iargs)
        if name not in providable_pos_key_parameters
        else _injectables[name]
        for name in pos_key_parameters
    }
    print(pos_key_arguments)
    remaining_args = list(iargs)
    # construct the varpos-arguments. If they can be provided, they take precedence on the passed as always
    if not var_pos_key_parameters and remaining_args:
        raise InjectionError(
            f"After constructing all positional parameters and injecting wherever possibly,"
            f"Function {f.__name__} has {len(remaining_args)} positionally given left over!"
        )
    var_pos_key_arguments = {}
    print("remaing args" + str(remaining_args))
    if var_pos_key_parameters:
        varpos_name = var_pos_key_parameters[0] or ""

        if remaining_args:
            var_pos_key_arguments = {varpos_name: remaining_args}
        # first check if it is given in the kwargs
        if varpos_name in kwargs:
            var_pos_key_arguments = {varpos_name: kwargs[varpos_name]}

        # then check if the varpos args are providable
        providable_var_pos_params = providable_parameters(var_pos_key_parameters)
        if not providable_var_pos_params and not var_pos_key_arguments:
            raise InjectionError(
                f"Function {f.__name__} expects variable positional-or-keyword parameter {varpos_name},"
                f"But has no arguments passed that are passed potionally, as keyword and is not injectable!."
            )
    print(var_pos_key_arguments)
    # key word arguments
    providable_keyword_only_parameters = providable_parameters(key_only_parameters)
    not_given_keyword_args = set(key_only_parameters).difference(
        providable_keyword_only_parameters.union(kwargs)
    )
    if not_given_keyword_args:
        raise InjectionError(
            f"Function {f.__name__} has keyword-only arguments {not_given_keyword_args}, that are not given and cannot be injected!"
        )
    key_only_argument_names = set(key_only_parameters).intersection(
        providable_keyword_only_parameters.union(kwargs)
    )
    key_only_arguments = {
        **{name: _injectables[name] for name in providable_keyword_only_parameters},
        **kwargs,
    }
    key_only_arguments = list(
        filter(lambda name: name in key_only_argument_names, key_only_arguments)
    )
    var_key_arguments = {
        name: kwargs[name]
        for name in list(
            filter(
                lambda name: name not in key_only_arguments
                and name not in pos_key_arguments
                and name not in var_pos_key_arguments,
                kwargs,
            )
        )
    }
    if var_key_parameters and not var_key_arguments:
        providable_var_key_params = providable_parameters(var_key_parameters)
        if not providable_var_key_params:
            raise InjectionError(
                f"Function {f.__name__} expects variable keyword parameter {var_key_parameters},"
                f"But has no arguments passed that are passed as keyword or are injectable!."
            )
        else:
            var_key_arguments = {
                name: _injectables[name] for name in providable_var_key_params
            }
    # print(
    #    f"After analysing function parameters, passed arguments and injectables, we've determined the function "
    #    f"signature to be: ({pos_only_arguments}, \, {pos_key_arguments}, *{var_pos_key_arguments}, {key_only_arguments}, **{var_key_arguments})"
    # )
    return (
        key_only_arguments,
        pos_key_arguments,
        pos_only_arguments,
        var_key_arguments,
        var_pos_key_arguments,
    )


def _inject_async(f):
    global _injectables
    (
        pos_only_parameters,
        pos_key_parameters,
        var_pos_key_parameters,
        key_only_parameters,
        var_key_parameters,
    ) = analyze_signature(f)

    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        (
            key_only_arguments,
            pos_key_arguments,
            pos_only_arguments,
            var_key_arguments,
            var_pos_key_arguments,
        ) = construct_arguments(
            f,
            pos_only_parameters,
            pos_key_parameters,
            var_pos_key_parameters,
            key_only_parameters,
            var_key_parameters,
            args,
            kwargs,
        )

        # todo
        return await f(
            *pos_only_arguments.values(),
            *pos_key_arguments.values(),
            *var_pos_key_arguments.values(),
            *key_only_arguments,
            **var_key_arguments,
        )

    return wrapper
