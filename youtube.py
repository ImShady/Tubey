from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

class Youtube():
    """Class that contains all of the youtube API related functions"""

    DEVELOPER_KEY = "AIzaSyAehWCYyOVH40G1uao5TTMv6ITNBq_xbEI"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def query(self, search_query):
        argparser.add_argument("--q", help="Search term", default=search_query)
        argparser.add_argument("--max-results", help="Max results", default=25)
        args = argparser.parse_args()
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
        playlists = []
        search_results = []

        try:
            search_results = search_response.get("items")
        except Exception as e:
            print("Error occurred! Could not find any items in search results!")
            print(e)

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for result in search_results:

          if result["id"]["kind"] == "youtube#video":

            videos.append("{} ({})".format(result["snippet"]["title"],result["id"]["videoId"]))

          elif result["id"]["kind"] == "youtube#channel":
            channels.append("{} ({})".format(result["snippet"]["title"],result["id"]["channelId"]))
          elif result["id"]["kind"] == "youtube#playlist":
            playlists.append("{} ({})".format (result["snippet"]["title"],result["id"]["playlistId"]))

        print("Videos:\n", "\n".join(videos), "\n")
        print("Channels:\n", "\n".join(channels), "\n")
        print("Playlists:\n", "\n".join(playlists), "\n")


if __name__ == "__main__":
    youtube = Youtube()
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()

    try:
        youtube.query(args)
    except HttpError as e:
      print("An HTTP error %d occurred:\n%s") % (e.resp.status, e.content)