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
    def __init__(cls, name, parents, dict):
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

        install_missing_dependencies(cls)
        return super(DependenciesMeta, cls).__init__(name, parents, dict)
