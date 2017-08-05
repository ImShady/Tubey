from youtube import Youtube


youtube_client = Youtube()
youtube_client.query("h3h3productions")

# from urllib.parse import quote
# from urllib.request import urlopen
# from bs4 import BeautifulSoup
#
# def search_youtube(search_query):
#
#     query = quote(search_query)
#     url = "https://www.youtube.com/results?search_query=" + query
#     response = urlopen(url)
#     html = response.read()
#     soup = BeautifulSoup(html, "html5lib")
#     for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
#         print('https://www.youtube.com' + vid['href'])
#
#
# search_youtube("h3h3productions")
