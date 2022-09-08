import os.path


def update_config(config_dictionary_instance):
    """
    Ensure that CI/CD builds do not used shared libraries for cartopy data_dir.

    See https://github.com/SciTools/cartopy/blob/63fd1e3ce7bc146a0e1a5b120441dabd4d38651c/lib/cartopy/__init__.py#L35 for explanation.
    """
    modified_config = config_dictionary_instance
    modified_config["data_dir"] = os.path.join(
        os.environ.get("CONDA_PREFIX"), "cartopy"
    )
    return modified_config
