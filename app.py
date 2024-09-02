import os
import sys
from pathlib import Path
from glob import glob

import importlib

from config import plugins_order


__version__ = "0.0.1"

# list of all registered plugins
# if pligin is not found, then None is placeholder
plugins = [None]*len(plugins_order)


for item in glob('plugins/*/*.py'):
    folder = Path(item).parent.parts[-1]
    if folder in plugins_order:
        index = plugins_order.index(folder)
        plugins[index] = importlib.import_module('plugins.'+folder).Plugin()


in_folder = None
out_folder = os.path.join(sys.argv[1], 'xml')


for plugin in plugins:
    if not plugin:
        print(f'Plugin {plugin_name} not found!')
        continue
    
    plugin_name = plugin.get_name()
    print(f'Plugin {plugin_name} is being used')

    in_folder = out_folder
    out_folder = os.path.join(sys.argv[1], plugin_name.lower())    

    # create output folder if it does not exist
    # ignore error if it already exists
    os.makedirs(out_folder, mode = 0o777, exist_ok = True)

    # if folder already exists, delete all files in it
    # for f in os.listdir(out_folder):
    #     # if f.endswith('.py'):
    #     os.remove(os.path.join(out_folder, f))

    plugin.process(in_folder, out_folder)

