from lib.config import Config
from slackclient import SlackClient
from flask import abort
from youtube import Youtube
from random import randint
from datetime import datetime
from lib.mysql import MySQL
from json import loads
from ast import literal_eval

class Tubey():

    buttons = [{
                    "name": "send",
                    "text": "Send",
                    "type": "button",
                    "style": "primary",
                    "value": "Send that pineapple"
                },
                {
                    "name": "next",
                    "text": "Next",
                    "type": "button",
                    "value": "NEXT!"
                },
                {
                    "name": "back",
                    "text": "Back",
                    "type": "button",
                    "value": "Back!"
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

    _youtube = Youtube()

    def __init__(self):
        # Cache the client in memory
        self._client = None
        self._mysql = MySQL(Config.get_variable('mysql_db', 'host'),
                             Config.get_variable('mysql_db', 'user'),
                             Config.get_variable('mysql_db', 'password'),
                             int(Config.get_variable('mysql_db', 'port')))

    def __send_message__(self, params, type="Message"):
        # Sends message to the user/channel
        # Type should either be Message or Ephemeral

        client = self.__get_client__()
        return client.api_call("chat.post" + type, **params)

    def suggest_video(self, user_info, team_info, channel_info, query="", action_info={}):
        # Sends a video suggestion in an ephemeral message

        if 'name' in action_info.keys() and action_info['name'] == 'next':
            button_value = loads(action_info['value']) # load value key of button which as a dict
            index = button_value['index'] # extract the index
            search_id = button_value['search_id'] # extract the search_id
            videos = self.__get_videos__(search_id) # fetch the list of videos for the corresponding search_id
            index = 0 if index == len(videos) - 1 else index + 1 # increment the index until list length then reset to 0
            suggested_video = self._youtube.get_video_metadata(videos[index])
            self.buttons[1]['value'] = '{{"index": {}, "search_id": {}}}'.format(index, search_id)
            self.buttons[2]['value'] = '{{"index": {}, "search_id": {}}}'.format(index, search_id)
            suggested_video['id'] = {"videoId": suggested_video['id']} # Will eventually get rid of this
            message_to_send = self.__build_message__(suggested_video, channel=channel_info['id'], user_id=user_info['id'])
            message_to_send['replace_original'] = True
            return message_to_send

        elif 'name' in action_info.keys() and action_info['name'] == 'back':
            button_value = loads(action_info['value'])  # load value key of button which as a dict
            index = button_value['index']  # extract the index
            search_id = button_value['search_id']  # extract the search_id
            videos = self.__get_videos__(search_id)  # fetch the list of videos for the corresponding search_id
            index = len(videos) - 1 if index == 0 else index - 1  # decrement the index until list length then reset to 0
            suggested_video = self._youtube.get_video_metadata(videos[index])
            self.buttons[1]['value'] = '{{"index": {}, "search_id": {}}}'.format(index, search_id)
            self.buttons[2]['value'] = '{{"index": {}, "search_id": {}}}'.format(index, search_id)
            suggested_video['id'] = {"videoId": suggested_video['id']}  # Will eventually get rid of this
            message_to_send = self.__build_message__(suggested_video, channel=channel_info['id'],
                                                     user_id=user_info['id'])
            message_to_send['replace_original'] = True
            return message_to_send

        elif 'name' in action_info.keys() and action_info['name'] == 'shuffle':
            search_id = action_info['value']
            videos = self.__get_videos__(search_id) # fetch the list of videos for the corresponding search_id
            num_vids = len(videos) # get length of videos (as of now, will always be <=25 from the YouTube API)
            suggested_video = self._youtube.get_video_metadata(videos[randint(0, num_vids) % num_vids])
            suggested_video['id'] = {"videoId": suggested_video['id']} # Will eventually get rid of this
            message_to_send = self.__build_message__(suggested_video, channel=channel_info['id'], user_id=user_info['id'])
            message_to_send['replace_original'] = True
            return message_to_send

        # This is the first call
        else:
            videos = self.search(query)
            suggested_video = videos[0]
            self.__insert_search__(videos=videos, query=query, user_info=user_info, team_name=team_info)
            message_to_send = self.__build_message__(suggested_video, channel=channel_info,
                                                     user_id=user_info['user_id'])
            response = self.__send_message__(message_to_send, type="Ephemeral")
            print(response)

    def send_video(self, user, video_id, channel):
        # Sends a chosen video to the channel
        params =  {
            "channel": channel,
            "text": "@{} shared a video!\nhttps://www.youtube.com/watch?v={}".format(user, video_id),
            "link_names": True
        }

        response = self.__send_message__(params)

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
        self.__send_message__(params)

    def search(self, search_query):
        results = self._youtube.query(search_query)

        return results['videos']

    def verify_token(self, token):
        verif_token = Config.get_variable('tubey', 'verif_token')

        # Validate the request parameters
        if token != verif_token:
            abort(401)  # Unauthorized request. If you're not Slack, go away

    def __get_client__(self):
        # Fetch a cached slack client or create one and return it
        # type is either 'bot' or 'user'
        if self._client is not None:
            return self._client

        token = Config.get_variable('tubey', 'oauth_token')
        sc = SlackClient(token)
        self._client = sc
        return sc

    def __insert_search__(self, user_info, team_name, videos, query):
        mysql = self._mysql
        mysql.execute("USE tubey;")
        video_ids = str([x['id']['videoId'] for x in videos]).replace("'", "\\'")
        table = Config.get_variable('mysql_db', 'table')
        insert_query = """
        INSERT INTO {} (user_name, user_id, search_query, videos, team_name)  VALUES ('{}', '{}', '{}', '{}', '{}')"""\
            .format(table, user_info['username'], user_info['user_id'], query, video_ids, team_name)

        mysql.execute(insert_query)
        mysql.commit()
        mysql.execute("SELECT * FROM {} WHERE search_id= LAST_INSERT_ID()".format(table))
        row_inserted = mysql.fetchone()
        search_id = row_inserted[0]
        self.buttons[1]['value'] = '{{"index": 0, "search_id": {}}}'.format(search_id)
        self.buttons[2]['value'] = '{{"index": 0, "search_id": {}}}'.format(search_id)
        self.buttons[3]['value'] = search_id

    def __build_message__(self, suggested_video, channel, user_id):

        published_date = datetime.strptime(suggested_video['snippet']['publishedAt'][0:10], "%Y-%m-%d").date().strftime(
            '%B %d, %Y')
        channel_name = suggested_video['snippet']['channelTitle']
        channel_id = suggested_video['id']['channelId']
        video_title = suggested_video['snippet']['title']
        description = suggested_video['snippet']['description']
        thumbnail = suggested_video['snippet']['thumbnails']['high']['url']
        video_id = suggested_video['id']['videoId']

        self.buttons[0]['value'] = id

        params = {
            'unfurl_links': False,
            'channel': channel,
            'user': user_id,
            "attachments": [{
                "title": "Video title: {}".format(video_title),
                "author_name": "{}".format(channel_name),
                "author_link": "https://www.youtube.com/channel/{}".format(channel_id),
                "text": "Published date: {}\nVideo description: {}".format(published_date, description),
                "title_link": "https://www.youtube.com/watch?v=".format(video_id),
                "image_url": thumbnail,
                "fallback": "You need to upgrade your Slack client to use this command!",
                "color": "#CD201F",
                "attachment_type": "default",
                "actions": self.buttons,
                "callback_id": "primary_menu"
            }]
        }

        return params

    def __get_videos__(self, search_id):
        self._mysql.execute("USE tubey;")
        table = Config.get_variable('mysql_db', 'table')
        self._mysql.execute("select videos from {} where search_id = {}".format(table, search_id))
        videos = literal_eval(self._mysql.fetchone()[0])

        return videos

if __name__ == "__main__":
    # Should probably put a legitimate sample run here...I'll start it off
    pass
