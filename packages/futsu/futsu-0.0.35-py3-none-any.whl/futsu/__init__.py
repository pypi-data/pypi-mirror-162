import futsu.lazy_import
import os

name = 'futsu'

DEFAULT_LAZY_ENABLE_SET = set([
    'FUTSU_GCP_ENABLE',
    'FUTSU_AWS_ENABLE',
])


def env_lazy_import(env_var, module_name):
    if env_var in os.environ:
        if os.environ[env_var].lower() in ['0', 'false']:
            return futsu.lazy_import.fake_import()
    else:
        if env_var not in DEFAULT_LAZY_ENABLE_SET:
            return futsu.lazy_import.fake_import()
    return futsu.lazy_import.lazy_import(module_name)
