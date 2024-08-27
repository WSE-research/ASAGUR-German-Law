import os
import sys

import importlib

from . import config


__version__ = "0.0.1"

# list of all registered plugins
plugins = []


for file in os.listdir('plugins'):
    if file.endswith('.py'):
        file = os.path.splitext(file)[0]
        plugins += [importlib.import_module('plugins.'+file).Plugin()]


def get_module_nr(module) -> int:
    name = module.__module__
    name = name.split('.')[-1]
    name = name.split('_')[0]
     
    return int(name, 16)


plugins.sort(key=lambda x:get_module_nr(x))

in_folder = None
out_folder = os.path.join(sys.argv[1], 'xml')


for plugin in plugins:
    plugin_name =  plugin.get_name()
    print(f'Plugin {plugin_name} is being used')

    in_folder = out_folder
    out_folder = os.path.join(sys.argv[1], plugin_name.lower())    

    # create output folder if it does not exist
    # ignore error if it already exists
    os.makedirs(out_folder, mode = 0o777, exist_ok = True)

    # if folder already exists, delete all files in it
    for f in os.listdir(out_folder):
        if f.endswith('.py'):
            os.remove(os.path.join(out_folder, f))

    plugin.process(in_folder, out_folder)


# in_dir = sys.argv[1]
# out_dir = sys.argv[2]
# endpoint = 'https://demos.swe.htwk-leipzig.de:40180/xml2rdf' # TODO: hide in secret
# # endpoint = 'http://localhost:5000/xml2rdf'


# import urllib3


# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# def XML_to_RDF(xml: str, dtd: str) -> str:
#     data = {
#         'xml': xml,
#         'dtd': dtd,
#         'prefix': 'urn:asagur',
#         'lang': 'de',
#     }
    
#     headers = {'content-type': 'application/json' }
#     r = requests.post(endpoint, headers=headers, json=data, allow_redirects=True, verify=False)
    
#     if r.status_code == 200:
#         return r.text
#     else:
#         return None
    

# def step000(in_folder: str, out_folder: str) -> None:
#     for file_name in pathlib.Path(in_folder).glob('*.dtd'):
#         with open(file_name, 'rt') as f:
#             dtd = f.read()
#         break
            
#     for file_name in pathlib.Path(in_folder).glob('*.xml'):
#         with open(file_name, 'rt') as f:
#             print(f'Processing {file_name}')

#             xml = f.read()
#             xml = xml.replace('<!DOCTYPE dokumente SYSTEM "http://www.gesetze-im-internet.de/dtd/1.01/gii-norm.dtd">', '')
            
#             rdf = XML_to_RDF(xml, dtd)
            
#             rdf_name = os.path.join(out_folder, str(file_name).split('/')[-1].split('.')[0]+'.ttl')
#             print(f'Writing {rdf_name}')

#             with open(rdf_name, 'wt') as g:
#                 g.write(rdf)


# print(f'Input folder: {in_dir}')
# print(f'Output folder: {out_dir}')
# print(f'Starting conversion...')
# step000(in_dir, out_dir)
