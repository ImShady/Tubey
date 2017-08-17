from lib.config import Config
from slackclient import SlackClient
from flask import abort
from youtube import Youtube
from random import randint
from datetime import datetime

class Tubey():

    buttons = [{
                    "name": "send",
                    "text": "Send",
                    "type": "button",
                    "style": "primary",
                    "value": "Send that pineapple"
                },
                {
                    "name": "shuffle",
                    "text": "Shuffle",
                    "type": "button",
                    "value": "Shuffle it up!"
                },
                {
                    "name": "cancel",
                    "text": "Cancel",
                    "type": "button",
                    "style": "danger",
                    "value": "Cancel dis plz"
                 }]

    def __init__(self):
        # Cache the client in memory
        self._client = None

    def send_message(self, params, type="Message"):
        # Sends message to the user/channel
        # Type should either be Message or Ephemeral
        client = self.get_client()
        client.api_call("chat.post" + type, **params)

    def get_client(self):
        # Fetch a cached slack client or create one and return it
        if self._client is not None:
            return self._client

        token = Config.get_variable('tubey', 'bot_oauth_token')
        sc = SlackClient(token)
        self._client = sc
        return self._client

    def suggest_video(self, query, channel, user, is_shuffle):
        # Sends a video suggestion in an ephemeral message
        videos = self.search(query)
        num_vids = len(videos)
        suggested_video = videos[randint(0, num_vids) % num_vids]

        published_date = datetime.strptime(suggested_video['snippet']['publishedAt'][0:10], "%Y-%m-%d").date().strftime(
            '%B %d, %Y')
        channel_name = suggested_video['snippet']['channelTitle']
        video_title = suggested_video['snippet']['title']
        description = suggested_video['snippet']['description']
        thumbnail = suggested_video['snippet']['thumbnails']['high']['url']
        id = suggested_video['id']['videoId']

        self.buttons[0]['value'] = id
        self.buttons[1]['value'] = query

        params = {
            'unfurl_links': False,
            'channel': channel,
            'user': user,
            "attachments": [{
                "title": "Video title: {}".format(video_title),
                "text": "Channel name: {}\nPublished date: {}\nVideo description: {}".format(channel_name, published_date, description),
                "title_link": "https://www.youtube.com/watch?v=".format(id),
                "image_url": thumbnail,
                "fallback": "You need to upgrade your Slack client to use this command!",
                "color": "#CD201F",
                "attachment_type": "default",
                "actions": self.buttons,
                "callback_id": "primary_menu"
            }]
        }

        if is_shuffle:
            params['replace_original'] = True
            return params
        else:
            response = self.send_message(params, type="Ephemeral")
            print(response)

    def send_video(self, video_id, channel):
        # Sends a chosen video to the channel
        params =  {
            "channel": channel,
            "text": "https://www.youtube.com/watch?v={}".format(video_id)
        }

        response = self.send_message(params)
        print(response)

        return {"delete_original": True}

    def send_channel(self, channel_id, channel_name, thumbnail_url):
        # Sends the youtube channel to the active user/slack channel
        channel_url = "https://www.youtube.com/channel/{}".format(channel_id)
        params = {'channel': 'tubeydev',
                  'text': "Here's the channel:",
                  'attachments': [
                      {'fallback': channel_name + ' thumbnail',
                       'title': channel_name,
                       "title_link": channel_url,
                       "image_url": thumbnail_url
                       }]
                  }
        self.send_message(params)

    def search(self, search_query):
        youtube = Youtube()
        results = youtube.query(search_query)

        return results['videos']

    def verify_token(self, token):
        verif_token = Config.get_variable('tubey', 'verif_token')

        # Validate the request parameters
        if token != verif_token:
            abort(401)  # Unauthorized request. If you're not Slack, go away

if __name__ == "__main__":
    # Should probably put a legitimate sample run here...I'll start it off
    pass
