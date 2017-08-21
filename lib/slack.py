from lib.config import Config
from slackclient import SlackClient
from flask import abort
from youtube import Youtube
from random import randint
from datetime import datetime
from lib.mysql import MySQL
from json import loads

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
        self._mysql = MySQL(Config.get_variable('mysql_db', 'host'),
                             Config.get_variable('mysql_db', 'user'),
                             Config.get_variable('mysql_db', 'password'),
                             int(Config.get_variable('mysql_db', 'port')))

    def send_message(self, params, type="Message"):
        # Sends message to the user/channel
        # Type should either be Message or Ephemeral

        client = self.__get_client__()
        return client.api_call("chat.post" + type, **params)

    def __get_client__(self):
        # Fetch a cached slack client or create one and return it
        # type is either 'bot' or 'user'
        if self._client is not None:
            return self._client

        token = Config.get_variable('tubey', 'oauth_token')
        sc = SlackClient(token)
        self._client = sc
        return sc

    def __insert_search__(self, username, team_name, videos, query):
        mysql = self._mysql
        mysql.execute("USE tubey;")
        video_ids = [x['id']['videoId'] for x in videos]
        print(video_ids)
        mysql.execute("INSERT INTO video_suggestions (username, search_query, videos) VALUES ('{}', '{}', '{}')"
                      .format(username, query, str(video_ids).replace("'", "\\'")))
        mysql.commit()
        mysql.execute("SELECT * FROM video_suggestions WHERE search_id= LAST_INSERT_ID()")
        row_inserted = mysql.fetchone()
        return row_inserted[0]

    def __build_message__(self, suggested_video, channel, username, search_id, index=0):

        published_date = datetime.strptime(suggested_video['snippet']['publishedAt'][0:10], "%Y-%m-%d").date().strftime(
            '%B %d, %Y')
        channel_name = suggested_video['snippet']['channelTitle']
        video_title = suggested_video['snippet']['title']
        description = suggested_video['snippet']['description']
        thumbnail = suggested_video['snippet']['thumbnails']['high']['url']
        id = suggested_video['id']['videoId']

        self.buttons[0]['value'] = id
        self.buttons[1]['value'] = '{{"index": {}, "search_id": {}}}'.format(index, search_id)

        params = {
            'unfurl_links': False,
            'channel': channel,
            'user': username,
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

        return params

    def suggest_video(self, user_info, team_info, channel_info, query="", action_info={}):
        # Sends a video suggestion in an ephemeral message
        if 'name' in action_info.keys() and action_info['name'] == 'shuffle':
            button_value = loads(action_info['value'])
            search_id = button_value['search_id']
            channel = channel_info['id']
            username = user_info['name']
            videos = self._mysql.execute("select videos from video_suggestions where search_id = {}".format(search_id))[0]
            num_vids = len(videos)
            suggested_video = videos[randint(0, num_vids) % num_vids]
            message_to_send = self.__build_message__(suggested_video, channel=channel,
                                                       username=username, search_id=search_id)
            message_to_send['replace_original'] = True
            return message_to_send
        else:
            videos = self.search(query)
            num_vids = len(videos)
            suggested_video = videos[randint(0, num_vids) % num_vids]
            search_id = self.__insert_search__(videos=videos, query=query, username=user_info, team_name=team_info)
            message_to_send = self.__build_message__(suggested_video, channel=channel_info,
                                                       username=user_info, search_id=search_id)
            response = self.send_message(message_to_send, type="Ephemeral")
            print(response)

    def send_video(self, user, video_id, channel):
        # Sends a chosen video to the channel
        params =  {
            "channel": channel,
            "text": "@{} shared a video!\nhttps://www.youtube.com/watch?v={}".format(user, video_id),
            "link_names": True
        }

        response = self.send_message(params)

        return {"delete_original": True}

    def send_channel(self, channel_id, channel_name, thumbnail_url):
        # Sends the youtube channel to the active user/slack channel
        params = {'channel': 'tubeydev',
                  'text': "Here's the channel:",
                  'attachments': [
                      {'fallback': channel_name + ' thumbnail',
                       'title': channel_name,
                       "title_link": "https://www.youtube.com/channel/{}".format(channel_id),
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
