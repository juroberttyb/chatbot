import configparser
config = configparser.ConfigParser()
config.read_file(open('default.cfg'))

tmp = config.sections()
print(dict(config['DEFAULT'].items()))

"""
for e in tmp:
    print(e)
    print(dict(config[e].items()))
"""
