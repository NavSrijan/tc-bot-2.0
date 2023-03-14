import toml
import ipdb


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

    def view_all_commands_with_roles(self):
        """Returns all the commands which have roles restriction."""
        try:
            return self.config['roles_list']
        except:
            return "There was some error."

    def view_command_role(self, command_name: str):
        """Returns all the roles allowed under a command."""
        try:
            return self.config['roles_list'][command_name]
        except:
            return "Couldn't find the command."

    def store_role(self, command_name: str, role_to_add: int):
        try:
            self.config['roles_list']
        except:
            self.config.update({'roles_list': {}})

        try:
            if role_to_add not in self.config['roles_list'][command_name]:
                self.config['roles_list'][command_name].append(role_to_add)
            else:
                pass
        except:
            self.config['roles_list'].update({command_name: role_to_add})

        self.dump_config()
        return role_to_add

    def remove_role(self, command_name, role_to_remove):
        roles = self.config['roles_list'][command_name].remove(role_to_remove)
        self.dump_config()
        return roles
