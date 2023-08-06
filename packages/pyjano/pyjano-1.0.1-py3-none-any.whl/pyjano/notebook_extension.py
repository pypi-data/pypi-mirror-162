import os
from pprint import pprint
import tornado.web
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler

import os

# i am big on absolute paths, so i made it return an absolute path
# also that makes the results clearer.
def full_path(dir_):
    if dir_[0] == '~' and not os.path.exists(dir_):
        dir_ = os.path.expanduser(dir_)
    return os.path.abspath(dir_)

class HelloWorldHandler(IPythonHandler):
    def get(self):
        self.finish('Hello, world!')


class CorsStaticFileHandler(tornado.web.StaticFileHandler):

    # def get(self, **other):
    #     pprint(other)
    #     return tornado.web.StaticFileHandler.get(**other)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get_content_type(self):
        # This is required for for jsroot to use partial file loading 
        return 'text/plain'

def load_jupyter_server_extension(nb_app):
    '''
    Register a hello world handler.

    Based on https://github.com/Carreau/jupyter-book/blob/master/extensions/server_ext.py
    '''


    web_app = nb_app.web_app

    nb_app.log.debug("=" * 30)
    nb_app.log.info('Setting Pyjano nb server extension')
    nb_app.log.debug(type(web_app))
    server_root_dir = full_path(web_app.settings['server_root_dir'])
    pprint(server_root_dir)
    # pprint(vars(web_app))
    print("=" * 30)


    host_pattern = '.*$'
    #route_pattern = url_path_join(web_app.settings['base_url'], '/hello')
    #web_app.add_handlers(host_pattern, [(route_pattern, tornado.web.StaticFileHandler)])

    web_app.add_handlers(host_pattern, [(r"/rjs/(.*)", CorsStaticFileHandler, {"path": server_root_dir, "default_filename": "README.md"})])
    #web_app.add_handlers(host_pattern, [(route_pattern, tornado.web.StaticFileHandler, {"path":r"/home/romanov/ceic/static"})])