import toml


class Config():

    def __init__(self, config_location="variables/config.toml"):
        self.config_location = config_location
        self.config = toml.load(self.config_location)

    def get_config(self):
        return self.config
    
    def dump_config(self):
        toml.dump(self.config, self.config_location)

    def add_blocked_url(self, url):
        urls = self.config['blocked_urls']['urls']
        urls.append(url)
        self.config['blocked_urls']['urls'] = urls
        self.dump_config()

    def remove_blocked_url(self, url):
        urls = self.config['blocked_urls']['urls']
        urls.remove(url)
        self.config['blocked_urls']['urls'] = urls
        self.dump_config()
