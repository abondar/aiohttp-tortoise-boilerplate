import yaml

with open("config.yml", 'r') as stream:
    config = yaml.load(stream)

MONGO_CONFIG = config.get('mongo')
