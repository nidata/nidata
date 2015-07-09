"""
"""
import sys


def install_dependency(module):
    import pip
    old_arg, sys.argv = sys.argv, ['pip', 'install', module]
    try:
        return pip.main() == 0
    except Exception as ex:
        print(ex)
        return False
    finally:
        sys.argv = old_arg


class DependenciesMeta(type):
    def __new__(cls, name, parents, props):
        def get_missing_dependencies(cls):
            missing_dependencies = []
            for dep in getattr(cls, 'dependencies', []):
                try:
                    __import__(dep)
                except ImportError as ie:
                    print('Import error: %s' % str(ie))
                    missing_dependencies.append(dep)
            return missing_dependencies

        def install_missing_dependencies(cls):
            print("Installing missing dependencies for %s" % str(cls))
            for dep in get_missing_dependencies(cls):
                if not install_dependency(dep):
                    raise Exception("Failed to install dependency '%s'." % dep)

        def __init__wrapper(init_fn):
            def wrapper_fn(self, *args, **kwargs):
                print self, args, kwargs
                install_missing_dependencies(self.__class__)
                return init_fn(self, *args, **kwargs)
            return wrapper_fn

        def super_init(cls):
            def wrapper_fn(self, *args, **kwargs):
                print "a"
                return super(cls, self).__init__(*args, **kwargs)
            return wrapper_fn

        new_cls = super(DependenciesMeta, cls).__new__(cls, name, parents, props)
        new_cls.__init__ = __init__wrapper(new_cls.__init__)
        return new_cls
