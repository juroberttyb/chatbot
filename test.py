"""
import configparser
cfg = configparser.ConfigParser()
cfg.read_file(open('default.cfg'))

tmp = cfg.sections()

cfg = cfg['DEFAULT']
cfg['server_port'] = '123'
# print(dict(cfg.items()))
"""

import json
with open('config.json') as config_file:
    python_dict = json.load(config_file)
print(python_dict)
print(bool(python_dict['reset_db']))
print(type(python_dict['data']['chat']['msg']))
# """


