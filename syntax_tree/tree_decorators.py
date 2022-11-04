import inspect

__all__ = ['on', 'when']


class Dispatcher(object):
    def __init__(self, param_name, wrapped_func):
        frame = inspect.currentframe().f_back.f_back
        self.param_index = self.__argspec(wrapped_func).args.index(param_name)
        self.param_name = param_name
        self.targets = {}

    def __call__(self, *args, **kwargs):
        type_ = args[self.param_index].__class__
        d_union = self.targets.get(type_)
        if d_union is not None:
            return d_union(*args, **kwargs)
        else:
            issub = issubclass
            t = self.targets
            ks = t.keys()
            ans = [t[k](*args, **kwargs) for k in ks if issub(type_, k)]
            if len(ans) == 1:
                return ans.pop()
            return ans

    def add_target(self, type_, target):
        self.targets[type_] = target

    @staticmethod
    def __argspec(wrapped_func):
        if hasattr(inspect, 'getfullargspec'):
            return inspect.getfullargspec(wrapped_func)
        else:
            return inspect.getargspec(wrapped_func)

def on(param_name):
    def wrapper_on(wrapped_func):
        dispatcher = Dispatcher(param_name, wrapped_func)
        return dispatcher
    return wrapper_on


def when(param_type_e):
    def wrapper_when(wrapped_func):
        frame = inspect.currentframe().f_back
        func_name = wrapped_func.func_name if 'func_name' in dir(wrapped_func) else wrapped_func.__name__
        dispatcher = frame.f_locals[func_name]
        if not isinstance(dispatcher, Dispatcher):
            dispatcher = dispatcher.dispatcher
        dispatcher.add_target(param_type_e, wrapped_func)

        def inner_wrapper_when(*args, **kwargs):
            return dispatcher(*args, **kwargs)
        inner_wrapper_when.dispatcher = dispatcher
        return inner_wrapper_when
    return wrapper_when

