from lib.config import Config
from slackclient import SlackClient

class Tubey():

    def __init__(self, **kwargs):
        # Cache the client in memory
        self._client = None


    def send_message(self, message):
        # Sends message to the user/channel
        params = {'channel': 'tubeydev', 'text': message}
        client = self.get_client()
        client.api_call("chat.postMessage", **params)


    def get_client(self):
        # Fetch a cached slack client or create one and return it
        if self._client is not None:
            return self._client

        token = Config.get_variable('tubey_credentials', 'bot_oauth_token')
        sc = SlackClient(token)
        self._client = sc
        return self._client


if __name__ == "__main__":

    tubey = Tubey()
    tubey.send_message("Sushi is great")
