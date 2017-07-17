import yaml

with open("config.yml", 'r') as stream:
    config = yaml.load(stream)
    
DB_CONFIG = config.get('bets_db')