from lib.config import Config
from slackclient import SlackClient

class Tubey():

    def __init__(self, **kwargs):
        # cache the client in memory
        self._client = None

    def send_message(self, message):
        raise NotImplemented

    def getClient(self):
        ### Fetch a cached slack client or create one and return it ###
        if self._client is not None:
            return self._client

        token = Config.get_variable('tubey_credentials', 'bot_oauth_token')
        sc = SlackClient(token)
        self._client = sc
        return self._client

if __name__ == "__main__":

    # params = {'channel': 'tubeydev', 'text': "Hi everybody! I'm a faige!"}
    # client.api_call("chat.postMessage", **params)
