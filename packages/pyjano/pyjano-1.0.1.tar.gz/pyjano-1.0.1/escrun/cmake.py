import os

from escrun.console_run_sink import ConsoleRunSink

from .test_env import is_notebook
from .runner import run, do_execute, sink_printer, stream_subprocess, console_printer


class CmakeBuildManager(object):
    def __init__(self, **kwargs):
        self.config = {}

        self.config.update(kwargs)  # update configs

        sink = self.config.get('sink', 'auto')
        if not sink:
            self.is_notebook = False
            self.sink = ConsoleRunSink()
        else:
            self.is_notebook = is_notebook()
            if (sink == 'auto' and self.is_notebook) or sink == 'notebook':
                # NotebookRunSink requires IPython which might not be installed if one only wants to work with console
                from escrun.notebook_run_sink import NotebookRunSink
                self.sink = NotebookRunSink()
            else:
                self.sink = ConsoleRunSink()

        default_build_prefix = os.path.join(__file__, 'cmake-build')
        self.config['build_prefix'] = self.config.get('build_prefix', default_build_prefix)

        self.config['install_prefix'] = self.config.get('install_prefix', default_build_prefix)
        self.runner = None

        # Automatically create build dir?
        self.config['auto_create_build_dir'] = self.config.get('auto_create_build_dir', False)

    def run_cmake_target(self, target, suffix='', retval_raise=False):
        """Builds G4E"""
        # Generate execution file        

        command = f"cmake --build {os.path.abspath(self.config['build_prefix'])} --target {target} {suffix}"
        
        self.sink.to_show = ["%]", "Error", "ERROR", "FATAL"]   # "[" - Cmake like "[9%]"
        self.sink.show_running_command(command)
        # if not self.sink.is_displayed:
        self.sink.display()

        retval, _,_,_ = run(command, self.sink, cwd=self.config['build_prefix'], retval_raise=retval_raise)
        return retval == 0


    def build(self, threads='auto', retval_raise=False):
        self.ensure_build_dir_exist()
        if threads == 'auto':
            import multiprocessing
            threads = multiprocessing.cpu_count()
            if threads > 2:
                threads -= 1
                
        suffix = f' -- -j {threads} -w '

        self.run_cmake_target(self.config['build_target'], suffix, retval_raise=retval_raise)

    def clean(self, retval_raise=False):
        self.run_cmake_target('clean', retval_raise=retval_raise)

    def ensure_build_dir_exist(self):
        if os.path.exists(self.config['build_prefix']):
            return      # Good! Nothing to add!

        # Create a directory?
        if self.config['auto_create_build_dir']:
            os.makedirs(self.config['build_prefix'], exist_ok=True)
            return

        # Probably it is an error
        err_msg = f"Error! CMake build path {self.config['build_prefix']} does not exist.\n"\
                  f"You may create it (if you sure it is right) with the command:\n"\
                  f"  mkdir -p {os.path.abspath(self.config['build_prefix'])}"
        raise ValueError(err_msg)

    def cmake_configure(self, build_type='RelWithDebInfo', silence_warnings=True, flags="", retval_raise=False):
        """
        Runs cmake configuration

        :param flags: CMake configuration flags like '-DCMAKE...'
        :param build_type:
        :param silence_warnings:
        :return:
        """
        self.ensure_build_dir_exist()

        if self.config.get('cxx_standard', ''):
            flags += ' -DCMAKE_CXX_STANDARD={}'.format(self.config['cxx_standard'])

        if self.config.get('install_prefix', ''):
            flags += ' -DCMAKE_INSTALL_PREFIX=' + os.path.abspath(self.config['install_prefix'])

        command = f"cmake {flags} -DCMAKE_BUILD_TYPE={build_type} {os.path.abspath(self.config['plugin_path'])}"
        self.sink.to_show = [">>>", "-- Configuring done", "-- Generating done", "Error"]  # "[" - Cmake like "[9%]"
        self.sink.show_running_command(command)

        # if not self.sink.is_displayed:
        self.sink.display()
        run(command, self.sink, cwd=self.config['build_prefix'], retval_raise=retval_raise)


    def _repr_html_(self):
        result_str = f"<strong>cmake build manager</strong><br>"
        return result_str
