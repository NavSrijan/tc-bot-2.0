import toml

class Config():

    def __init__(self, config_location="variables/config.toml"):
        self.config_location = config_location
        self.config = toml.load(self.config_location)

    def get_config(self):
        return self.config

    def dump_config(self):
        # toml_string = toml.dump(self.config)
        with open(self.config_location, "w") as toml_file:
            toml.dump(self.config, toml_file)

    def add_blocked_url(self, url):
        urls = self.config['blocked_urls']['urls']
        urls.append(url)
        self.config['blocked_urls']['urls'] = urls
        self.dump_config()
        return urls

    def remove_blocked_url(self, url):
        urls = self.config['blocked_urls']['urls']
        urls.remove(url)
        self.config['blocked_urls']['urls'] = urls
        self.dump_config()
        return urls
