import pkgutil
from importlib.metadata import distributions



def get_all_addons():
    try:
        package_path = __path__
        package_name = __name__
        modules = []
        for module_info in pkgutil.iter_modules(package_path, package_name + '.'):
            modules.append(module_info.name)
        return modules
    except AttributeError:
        return []  # Not a packag
    

