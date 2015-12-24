"""
Functions for dynamically managing dependencies.
"""
import sys


def install_dependency(module):
    """
    TODO: install_dependency docstring.
    """
    import pip
    old_arg, sys.argv = sys.argv, ['pip', 'install', module]
    try:
        return pip.main() == 0
    except Exception as ex:
        print(ex)
        return False
    finally:
        sys.argv = old_arg


def get_missing_dependencies(dependencies):
    """
    TODO: get_missing_dependencies docstring
    """
    missing_dependencies = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError as ie:
            print('Import error: %s' % str(ie))
            missing_dependencies.append(dep)
    return missing_dependencies


class DependenciesMeta(type):
    """
    TODO: DependenciesMeta docstring.
    """
    def __new__(cls, name, parents, props):
        def get_cls_missing_dependencies(cls):
            """
            TODO: get_missing_dependencies docstring
            """
            return get_missing_dependencies(
                getattr(cls, 'dependencies', []))

        def install_missing_dependencies(cls):
            """
            TODO: install_missing_dependencies docstring
            """
            for dep in get_cls_missing_dependencies(cls):
                print("Installing missing dependencies '%s', for %s" % (
                    dep, str(cls)))
                if not install_dependency(dep):
                    raise Exception("Failed to install dependency '%s'; "
                                    "you will need to install it manually "
                                    "and re-run your code." % dep)

        def _init__wrapper(init_fn):
            """
            TODO: _init__wrapper docstring
            """
            def wrapper_fn(self, *args, **kwargs):
                install_missing_dependencies(self.__class__)
                return init_fn(self, *args, **kwargs)
            return wrapper_fn

        def super_init(cls):
            """
            TODO: super_init docstring
            """
            def wrapper_fn(self, *args, **kwargs):
                return super(cls, self).__init__(*args, **kwargs)
            return wrapper_fn

        new_cls = super(DependenciesMeta, cls) \
            .__new__(cls, name, parents, props)
        new_cls.__init__ = _init__wrapper(new_cls.__init__)
        return new_cls
