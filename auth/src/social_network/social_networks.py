from .networks import TYPE_NETWORKS, networks


class SocialNetworks:

    def __init__(self, network_name: str):
        try:
            self.network: TYPE_NETWORKS = networks[network_name]()
        except KeyError:
            raise ValueError(f"Invalid network name {network_name}")

    def __repr__(self):
        return f"<{self.network.network_name}>"

    @property
    def auth_url(self) -> str:
        return self.network.auth_url

    def get_user_data(self, code: int) -> dict:
        return self.network.get_user_data(code)
