# A plugin generator

from .mini_plugin_generator import generate_mini_analysis_plugin

plugin_generators = {
    'mini_analysis': generate_mini_analysis_plugin
}


def generate_plugin(plugin_type, **params):
    """ Generates a directory with jana plugin.

    Known plugin types:
        mini_analysis

    Usual parameters:
        plugin_name - snake_case defined name (directory name will correspond to it)
        class_name  - CamelCase defined name (Related C++ class names will have this name)
        path        - Path to the directory with plugin, otherwise current dir is used

    """

    # check if this plugin generator is known
    if plugin_type not in plugin_generators:
        message = f"plugin_type provided to generate_plugin function is unknown. Please use one of: " +\
                    " ".join([name for name in plugin_generators.keys()])
        raise ValueError(message)

    plugin_generators[plugin_type](**params)