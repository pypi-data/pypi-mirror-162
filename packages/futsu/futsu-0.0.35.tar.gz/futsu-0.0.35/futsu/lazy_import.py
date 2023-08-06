import importlib


def lazy_import(name):
    return LazyImport(name)


class LazyImport:

    import_dict = {}

    def __init__(self, name):
        self.name = name

    def load(self):
        if self.name not in LazyImport.import_dict:
            LazyImport.import_dict[self.name] = {
                'success': False,
                'module': None,
            }
            m = importlib.import_module(self.name)
            LazyImport.import_dict[self.name]['module'] = m
            LazyImport.import_dict[self.name]['success'] = True

        return LazyImport.import_dict[self.name]['module']


def fake_import():
    return FakeImport()


class FakeImport:

    def __init__(self):
        pass

    def load(self):
        return None
