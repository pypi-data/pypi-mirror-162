"""Pyjano stands for Python Jana Orchestrator

Jana(nthreads=10, )
"""
import os


import escrun
from escrun.console_run_sink import ConsoleRunSink



#
# class ConsoleRunSink:
#     def add_line(self, line):
#         print(line)
#
#     def display(self):
#         print("Rendering in console")
#
#     def done(self):
#         pass
#
#     def show_running_command(self, command):
#         print(f'Command = "{command}"')
#
#     @property
#     def is_displayed(self):
#         return True
#
#
# from IPython.core.display import display
# from ipywidgets import widgets
#
#
# class NotebookRunSink:
#
#     def __init__(self):
#         self._output_widget = widgets.Output()
#         self._is_displayed = True
#         self._label = widgets.Label(value="Initializing...")
#         self._stop_button = widgets.Button(
#             description='Terminate',
#             disabled=False,
#             button_style='',  # 'success', 'info', 'warning', 'danger' or ''
#             tooltip='Terminate jana process',
#             # icon='check'
#         )
#         self._command_label = widgets.HTML()
#
#     # noinspection PyTypeChecker
#     def display(self):
#         # title_widget = widgets.HTML('<em>Vertical Box Example</em>')
#         self._stop_button.layout.display = ''
#         control_box = widgets.HBox([self._stop_button, self._label])
#
#         accordion = widgets.Accordion(children=[self._output_widget, self._command_label], selected_index=None)
#         accordion.set_title(0, 'Full log')
#         accordion.set_title(1, 'Run command')
#
#         vbox = widgets.VBox([control_box, accordion])
#
#         # display(accordion)
#         display(vbox)
#         self._is_displayed = True
#
#     def add_line(self, line):
#         to_show = [
#             'Initializing plugin',
#             'Start processing',
#             'Completed events',
#             'ERROR',
#             'FATAL',
#             '[INFO]'
#         ]
#
#         tokens = line.split('\n')
#         for token in tokens:
#             for test in to_show:
#                 if test in token:
#                     self._label.value = token
#
#         self._output_widget.append_stdout(line + '\n')
#
#     def done(self):
#         self._stop_button.layout.display = 'none'
#
#     def show_running_command(self, command):
#         tokens = shlex.split(command)
#         self._command_label.value = '<br>'.join(tokens)
#
#     @property
#     def is_displayed(self):
#         return self._is_displayed
#
#
# def _run(command, sink):
#     """Wrapper around subprocess.Popen that returns:
#
#     :return retval, start_time, end_time, lines
#     """
#     if isinstance(command, str):
#         command = shlex.split(command)
#
#     # Pretty header for the command
#     sink.add_line('=' * 20)
#     sink.add_line("RUN: " + " ".join(command))
#     sink.add_line('=' * 20)
#
#     # Record the start time
#     start_time = datetime.now()
#     lines = []
#
#     # stderr is redirected to STDOUT because otherwise it needs special handling
#     # we don't need it and we don't care as C++ warnings generate too much stderr
#     # which makes it pretty much like stdout
#     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     while True:
#         line = process.stdout.readline().decode('latin-1').replace('\r', '\n')
#
#         if process.poll() is not None and line == '':
#             break
#         if line:
#             if line.endswith('\n'):
#                 line = line[:-1]
#             sink.add_line(line)
#             lines.append(line)
#
#     # Get return value and finishing time
#     retval = process.poll()
#     end_time = datetime.now()
#     sink.done()
#
#     sink.add_line("------------------------------------------")
#     sink.add_line(f"RUN DONE. RETVAL: {retval} \n\n")
#     if retval != 0:
#         sink.add_line(f"ERROR. Retval is not 0. Plese, look at the logs\n")
#
#     return retval, start_time, end_time, lines
from escrun.runner import run
from escrun.test_env import is_notebook
from .plugin import PluginFromSource, Plugin


class Jana(object):
    """Jana - class allows to configure and run ejana (and genue JANA) processes.
    It also provides IPython widgets for interactive control over jana from Jupyter
    """

    static_content_is_inserted = False

    server = None

    def __init__(self, gui='auto', **kwargs):
        self.config = {}

        if not gui:
            self.is_notebook = False
            self.sink = ConsoleRunSink()
        else:
            self.is_notebook = is_notebook()
            if (gui == 'auto' and self.is_notebook) or gui == 'notebook':
                from escrun.notebook_run_sink import NotebookRunSink
                self.sink = NotebookRunSink()
            else:
                self.sink = ConsoleRunSink()

        self.sink.to_show = ["%]", "Error", "ERROR", "FATAL"]  # "[" - Cmake like "[9%]"
        self.runner = None

        self.exec_path = 'ejana'
        self.plugin_search_paths = []
        self.config['params'] = {}
        self.config['params'].update(kwargs)

        self.config['plugins'] = {}
        self.config['flags'] = []
        self.config['input_files'] = []

        self._environ_is_updated = False

    def update_environment(self):
        """Updates the environment according to the configuration"""
        def print_plugin_locations(locations):
            for loc in locations:
                self.sink.add_line(f"   {loc}")

        ex_plugin_locations = [loc for loc in os.environ.get('JANA_PLUGIN_PATH', '').split(':') if loc]
        if ex_plugin_locations and ex_plugin_locations[0]:
            self.sink.add_line("Existing plugin locations")
            print_plugin_locations(ex_plugin_locations)

        if self.plugin_search_paths:
            self.sink.add_line("Appending them by plugin search locations")
            print_plugin_locations(self.plugin_search_paths)

        # remove a location from existing locations. We will prepend the list anyway

        env_plugin_path = ':'.join(self.plugin_search_paths + ex_plugin_locations)
        os.environ['JANA_PLUGIN_PATH'] = env_plugin_path
        # print(os.environ['JANA_PLUGIN_PATH'])
        self._environ_is_updated = True

    def add_plugin_paths(self, plugin_paths):
        """Set additional paths where JANA looks for plugins"""
        # The later plugin location will have greater load priority
        # This means that it must be earlier in the list

        if isinstance(plugin_paths, str):
            plugin_paths = [plugin_paths]

        for path in plugin_paths:
            self.plugin_search_paths.insert(0, path)

        self._environ_is_updated = False



    def plugin(self, plugin, **plugin_args):
        """
        Adds (activates) a plugin with a given name.
        This function may stack: .plugin('a').plugin('b')

        Example: jana.plugin('eic_smear', verbose=2, detector='beast')
                     .plugin('eventless_writer')

        :param plugin: Name of the plugin to activate
        :param plugin_args: Plugin arguments
        :return:
        """

        if plugin == 'jana' and plugin_args:
            self.config['params'].update(plugin_args)
            return self

        # It just a plugin name like:
        # .plugin('vmeson', ...)
        if isinstance(plugin, str):
            self.config['plugins'][plugin] = Plugin(plugin, **plugin_args)
            return self

        # Making sure that plugin is from Plugin
        assert isinstance(plugin, Plugin)

        # Update args
        self.config['plugins'][plugin.name] = plugin
        plugin.args.update(plugin_args)

        # Do we need to append search path?
        if plugin.search_path and plugin.search_path not in self.plugin_search_paths:
            self.plugin_search_paths.append(plugin.search_path)
            self._environ_is_updated = False    # this will trigger regenerating env

        # replace sink if needed
        if isinstance(plugin, PluginFromSource):
            plugin.builder.sink = self.sink

        return self

    def source(self, source_strings):
        """Input source (usually files) configuration.

        This function stacks with plugins and another source

        ```python
        jana.plugin('beagle_reader') \
            .source('file1.txt')     \
            .source(['file2.txt', 'file3.txt'])
        ```
        """

        if isinstance(source_strings, str):
            self.config['input_files'].append(source_strings)
        else:
            self.config['input_files'].extend(source_strings)

        return self

    def reset_plugins(self):
        """
        Resets the plugin configuration
        """

        self.config['plugins'] = {}
        return self

    def configure_plugins(self, plugins):
        """ Configures plugins (using dicts). Replaces the previous configuration.

        :param plugins:
        :return: dict with plugins config
        """
        self.reset_plugins()

        if not plugins:
            return self.config['plugins']

        def _update(plugin_name, plugin_data):
            if plugin_name == 'jana' and plugin_data:
                self.config['params'] = plugin_data
            else:
                self.config['plugins'][plugin_name] = plugin_data

        assert isinstance(plugins, list)
        for item in plugins:
            if isinstance(item, str):
                _update(item, {})
            elif isinstance(item, tuple) or isinstance(item, list):
                # plugin in form:
                # ('name', {config})
                assert isinstance(item[1], dict)
                _update(item[0], item[1])
            else:
                assert isinstance(item, dict)
                # dict must be with one key like:
                # {'beagle_reader': { ... configs ... }}
                plugin_name = list(item)[0]
                _update(plugin_name, item[plugin_name])

        return self.config['plugins']

    def configure(self, plugins=None, flags=None, files=None, params=None, plugin_paths=None):
        """Universal configuration function

        (!) this function resets and overwrites the configuration made by functions like plugin, input, etc

        Example:

        jana.configure(
        plugins=[  # a list of plugins to use:
            'beagle_reader',  # plugin name, no additional parameters
            {'open_charm': {  # add vmeson plugin & set '-Pvmeson:verbose=2' parameter
                'verbose': 1,  # Set verbose mode for that plugin
                'smearing': 1}  # Set smearing mode
            },
            {'eic_smear': {
                    'verbose': 1,
                    'detector': 'jleic'
                }
            }
        ],
        files=["/home/romanov/ceic/data/herwig6_e-p_5x100.hepmc"],  # or [list, of, files]
        params={'nthreads': 4, 'nevents': 2000}  # for parameters that don't follow <plugin>:<name> naming
                                                 # Smart enough to run it like --nthreads=8
    )  # instead of -P...


        :param plugins: list of plugins
        :param flags: list of raw flags (will be added to launch arguments without formatting)
        :param files: list of input files
        :param params: list of parameters (will be added with -P<name>=<value> flag)
        :param plugin_paths: Additional paths to search for plugins
        """
        if plugins:
            self.configure_plugins(plugins)
        if params:
            if self.config['params']:
                self.config['params'].update(params)
            else:
                self.config['params'] = params
        if flags:
            self.config['flags'] = flags
        if files:
            self.config['input_files'] = files

        if plugin_paths:
            self.add_plugin_paths(plugin_paths)

        # noinspection PyTypeChecker
        if self.is_notebook:
            # display(Javascript('console.log("hello world")', lib='https://code.jquery.com/jquery-3.4.1.slim.js'))
            clear_output()
            # noinspection PyTypeChecker
            display(HTML('<b>JANA</b> configured...'))

    # noinspection PyTypeChecker
    def interactive_notebook(self):
        """Installs scripts and styles for page that enables interactive widgets

          Obsoletes within Jupyter lab ^1.0.2
         """

        '/static/css/bootstrap.min.css'

        display(HTML("""        
        <link rel="stylesheet" href="/static/css/bootstrap.min.css" crossorigin="anonymous">
        <script src="/static/js/bootstrap.min.js"></script>        
        <script src="/static/js/plugins.js"></script>        
        <link rel="stylesheet" href="/static/css/pretty-checkbox.min.css">
        '<b>Pyjano</b> jupyter notebook interactive loaded...'        
        """))

    # noinspection PyTypeChecker
    def plugins_gui(self):
        """Shows interactive GUI, which helps configure plugins and their parameters"""

        self.interactive_notebook()

        from pyjano.server.jana import offline_render
        display(widgets.HTML(offline_render()))
        display(Javascript("""
            if(typeof jQuery=='undefined') {
                var headTag = document.getElementsByTagName("head")[0];
                var jqTag = document.createElement('script');
                jqTag.type = 'text/javascript';
                jqTag.src = '/static/jsroot/libs/jquery.js';
                jqTag.onload = activatePluginsGui;
                headTag.appendChild(jqTag);
            } else {
                 activatePluginsGui();
            }
                """))

    def run(self, retval_raise=False):
        """Runs ejana/JANA process """
        if not self._environ_is_updated:
            self.update_environment()

        # if not self.sink.is_displayed:
        self.sink.display()

        # Build plugins?
        for plugin in self.config['plugins'].values():
            if isinstance(plugin, PluginFromSource):
                do_str = "CMake configuration"
                try:
                    plugin.builder.cmake_configure(retval_raise=True)
                    do_str = "compilation"
                    plugin.builder.build(retval_raise=True)
                except RuntimeError:
                    self.sink.add_line(f"[FATAL] during plugin '{plugin.name}' {do_str}. Look at logs/output for details")
                    return

        # apply to_show for ejana
        self.sink.to_show = [
                    'Initializing plugin',
                    'Start processing',
                    'Completed events',
                    'ERROR',
                    'FATAL',
                    '[INFO] Status:',
                    '[INFO] Start',
                    '[INFO] JPluginLoader',
                ]

        command = f"""{self.exec_path} {self.get_run_command()} -Pjana:debug_plugin_loading=1 """
        self.sink.show_running_command(command)

        # RuN
        run(command, self.sink, retval_raise=retval_raise)

    def get_run_command(self):
        """Returns the command, which is used to execute jejana"""
        add_plugins_str = "-Pplugins=" + ",".join(self.config['plugins'].keys())
        plugins_params_str = " -Pnthreads=1"
        for plugin in self.config['plugins'].values():
            for name, value in plugin.args.items():
                plugins_params_str += f' -P{plugin.name}:{name}={value}'

        params_str = " ".join([f'-P{name}={value}' for name, value in self.config['params'].items()])
        files_str = " ".join([file for file in self.config['input_files']])
        flags_str = " ".join([flag for flag in self.config['flags']])
        return f'{add_plugins_str} {plugins_params_str} {params_str}  {files_str} {flags_str}'

    def _repr_html_(self):
        plugins_str = ",".join(self.config['plugins'].keys())

        result_str = f"<strong>eJana</strong> configured<br><strong>plugins:</strong> {plugins_str}"
        if self.config['input_files']:
            sources_str = "<br>".join(self.config['input_files'])
            result_str += f"<br><strong>sources:</strong><br>{sources_str}"
        return result_str


if __name__ == "__main__":
    jana = Jana()
    jana.configure(
        plugins=[  # a list of plugins to use:
            'beagle_reader',  # plugin name, no additional parameters
            {'open_charm': {  # add vmeson plugin & set '-Pvmeson:verbose=2' parameter
                'verbose': 1,  # Set verbose mode for that plugin
                'smearing': 1}  # Set smearing mode
            },
            {'eic_smear': {
                    'verbose': 1,
                    'detector': 'jleic'
                }
            }
        ],
        files=["/home/romanov/ceic/data/herwig6_e-p_5x100.hepmc"],
        # or [list, of, files]
        params={'nthreads': 4, 'nevents': 2000}  # for parameters that don't follow <plugin>:<name> naming
        # Smart enough to run it like --nthreads=8
    )  # instead of -P...

    print(jana.get_run_command())
