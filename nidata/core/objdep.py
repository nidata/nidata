"""
Functions for dynamically managing dependencies.
"""

import sys

import pip
from six import with_metaclass


def install_dependency(module_name, install_info=None, verify=True):
    """
    TODO: install_dependency docstring.
    """
    install_info = install_info or module_name

    # Install it.
    old_arg, sys.argv = sys.argv, ['pip', 'install', install_info]
    try:
        if not pip.main() == 0:
            return False
    except Exception as ex:
        print("Exception while installing %s: %s" % (module_name, ex))
        return False
    finally:
        sys.argv = old_arg

    # Verify it
    if verify:
        try:
            __import__(module_name)
        except ImportError as ie:
            print('Failed to import %s: %s' % (module_name, ie))
            return False

    return True


def get_missing_dependencies(dependencies):
    """
    TODO: get_missing_dependencies docstring
    """
    missing_dependencies = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:  # as ie:
            # print('Import error: %s' % str(ie))
            missing_dependencies.append(dep)
    return missing_dependencies


class DependenciesMeta(type):
    """
    TODO: DependenciesMeta docstring.
    """
    def __new__(cls, name, parents, props):
        def _init__wrapper(init_fn):
            """
            TODO: _init__wrapper docstring
            """
            def wrapper_fn(self, *args, **kwargs):
                self.__class__.install_missing_dependencies()
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


class ClassWithDependencies(with_metaclass(DependenciesMeta, object)):
    @classmethod
    def get_missing_dependencies(cls):
        """
        TODO: get_missing_dependencies docstring
        """
        return get_missing_dependencies(
            getattr(cls, 'dependencies', ()))

    @classmethod
    def install_missing_dependencies(cls, dependencies=None):
        """
        TODO: install_missing_dependencies docstring
        """
        if dependencies is None:
            dependencies = cls.get_missing_dependencies()
        for dep in dependencies:
            print("Installing missing dependencies '%s', for %s" % (
                dep, str(cls)))

            # Allow install info to be a dict; value is some
            # alternate pip string for installing the module name.
            # (e.g. git+git://github.com/gldnspud/virtualenv-pythonw-osx)
            install_info = None
            if isinstance(cls.dependencies, dict):
                install_info = cls.dependencies[dep]

            if not install_dependency(dep, install_info=install_info):
                raise Exception("Failed to install dependency '%s'; "
                                "you will need to install it manually "
                                "and re-run your code." % dep)
