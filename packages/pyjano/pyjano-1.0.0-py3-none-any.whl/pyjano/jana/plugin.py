import os

from escrun.cmake import CmakeBuildManager


class PluginCmakeBuildManager(CmakeBuildManager):
    def __init__(self, plugin_path, **kwargs):

        if not plugin_path:
            raise RuntimeError("plugin_path is not provided")
        if not os.path.isdir(plugin_path):
            raise RuntimeError("plugin_path is not a directory (or the permission is denied)")

        kwargs['plugin_path'] = plugin_path

        # Plugin name
        if 'name' not in kwargs:
            kwargs['name'] = os.path.basename(os.path.abspath(plugin_path))

        default_build_prefix = os.path.join(plugin_path, 'cmake-build')
        kwargs['build_prefix'] = kwargs.get('build_prefix', default_build_prefix)
        kwargs['install_prefix'] = kwargs.get('install_prefix', plugin_path)
        kwargs['build_target'] = kwargs.get('build_target', kwargs['name']+'_plugin')

        # For plugins set it true
        kwargs['auto_create_build_dir'] = kwargs.get('auto_create_build_dir', True)

        super().__init__(**kwargs)


class Plugin(object):
    def __init__(self, name, **kwargs):

        if not name:
            raise ValueError("Plugin name is emtpy or None. Plugin name is required")
        self._name = name

        self.args = {}
        self.args.update(kwargs)

    @property
    def name(self):
        return self._name

    @property
    def search_path(self):
        return None


class PluginFromSource(Plugin):
    """Jana plugin from """
    def __init__(self, plugin_path, **kwargs):
        self.builder = PluginCmakeBuildManager(plugin_path, **kwargs)
        self.builder.config['build_target'] = 'install'
        self.builder.config['cxx_standard'] = '17'
        self.args = {}
        super().__init__(self.builder.config['name'])

    @property
    def name(self):
        return self.builder.config['name']

    @property
    def search_path(self):
        return self.builder.config['install_prefix']

# class UserPlugin(object):
#     def