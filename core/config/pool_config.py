from configparser import RawConfigParser
from pathlib import Path


class PoolConfig:
    def __init__(self):
        self.home = str(Path.home())
        env_path = self.home+'/cactus-pool/core/config/pool_config.ini'

        config = RawConfigParser()
        if (len(config.read(env_path)) == 0):
            self.error = True
        else:
            self.error = False
            self.static(config)
            self.delegate(config)
            self.pool(config)
            self.logging(config)

    def static(self, c):
        self.atomic = int(c.get('static', 'atomic'))
        self.network = c.get('static', 'network')
        self.username = c.get('static', 'username')

    def delegate(self, c):
        self.delegate = c.get('delegate', 'delegate')

    def pool(self, c):
        self.pool_ip = c.get('pool', 'pool_ip', fallback="127.0.0.1")
        self.pool_port = c.get('pool', 'pool_port', fallback="5000")
        self.pool_template = c.get('pool', 'pool_template', fallback="bfx")
        self.explorer = c.get('pool', 'explorer', fallback="https://texplorer.solar.org")
        self.coin = c.get('pool', 'coin', fallback="tSXP")
        self.proposal1 = c.get('pool', 'proposal1', fallback="https://delegates.solar.org/delegates/xxxx")
        self.proposal2 = c.get('pool', 'proposal2', fallback="https://yy.yy.yy/")
        self.proposal2_lang = c.get('pool', 'proposal2_lang', fallback="LANG")

    def logging(self, c):
        self.loglevel = c.get('logging', 'loglevel')
        self.formatter = c.get('logging', 'formatter')
