from googleapiclient.discovery import build
import json
import argparse
import requests
from lib.config import Config

class Youtube():
    """Class that contains all of the youtube API related functions"""

    DEVELOPER_KEY = Config.get_variable('youtube_api', 'dev_key')
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def query(self, search_query):
        parser = argparse.ArgumentParser(prog='PROG', conflict_handler='resolve')
        parser.add_argument("--q", help="Search term", default=search_query)
        parser.add_argument("--max-results", help="Max results", default=25)
        args, unknown = parser.parse_known_args()
        options = args
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
          developerKey=self.DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
          q=options.q,
          part="id,snippet",
          maxResults=options.max_results
        ).execute()

        videos = []
        channels = []
        search_results = []

        try:
            search_results = search_response.get("items")
        except Exception as e:
            print("Error occurred! Could not find any items in search results!")
            print(e)

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, and channels
        for result in search_results:

          if result["id"]["kind"] == "youtube#video":
              videos.append(result)
          elif result["id"]["kind"] == "youtube#channel":
              channels.append(result)

        results = {"videos": videos, "channels": channels}

        return results

    def get_video_metadata(self, video_id):
        payload = {'id': video_id, 'part': 'snippet', 'key': self.DEVELOPER_KEY}
        response = requests.get('https://www.googleapis.com/youtube/v3/videos', params=payload)
        return json.loads(response.content.decode("utf-8"))['items'][0]


if __name__ == "__main__":
    youtube = Youtube()
    results = youtube.query("rick and morty")
    print(results['videos'])
