# plugin for german law ontology project
# the plugin converts XML file to RDF
# input: all XML files in a folder (in_folder)
# output: TTL file for each XML file (out_folder)

import os
import pathlib
import requests
import urllib3

from .config import endpoint


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def XML_to_RDF(xml: str, dtd: str) -> str:
    data = {
        'xml': xml,
        'dtd': dtd,
        'prefix': 'urn:asagur',
        'lang': 'de',
    }
    
    headers = {'content-type': 'application/json' }
    r = requests.post(endpoint, headers=headers, json=data, allow_redirects=True, verify=False)
    
    if r.status_code == 200:
        return r.text
    else:
        return None


def step(in_folder: str, out_folder: str) -> None:
    for file_name in pathlib.Path(in_folder).glob('*.dtd'):
        with open(file_name, 'rt') as f:
            dtd = f.read()
        break
            
    for file_name in pathlib.Path(in_folder).glob('*.xml'):
        with open(file_name, 'rt') as f:
            print(f'Processing {file_name}')

            xml = f.read()
            xml = xml.replace('<!DOCTYPE dokumente SYSTEM "http://www.gesetze-im-internet.de/dtd/1.01/gii-norm.dtd">', '')
            
            rdf = XML_to_RDF(xml, dtd)
            
            rdf_name = os.path.join(out_folder, str(file_name).split('/')[-1].split('.')[0]+'.ttl')
            print(f'Writing {rdf_name}')

            with open(rdf_name, 'wt') as g:
                g.write(rdf)


class Plugin:
    @staticmethod
    def get_name() -> str:
        return 'XML_2_RDF'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)
