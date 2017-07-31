from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import urllib.request, json, csv

API_KEY = "API KEY HERE"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtubeAPI(options):
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
		developerKey = API_KEY)

	#Make a request to get ID of videos
	search_response = youtube.search().list(
		q = options.q,
		part = "id",
		maxResults = options.max_results
		).execute()
	
	# Since v3 only returns up to 50 results, to get more than 50 results we have to use nextPageToken. 
	'''
	nextPageToken = search_response.get('nextPageToken')
	while('nextPageToken' in search_response):
		nextPage = youtube.search().list(
			q = options.q,
			part = "id",
			maxResults = options.max_results
			).execute()
		search_response['item'] = search_response['items'] + nextPage['items']

		if 'nextPageToken' not in nextPage:
				search_response.pop('nextPageToken', None)
		else:
			nextPageToken = nextPage['nextPageToken']

	'''
	
	#Generate list of video IDs
	videos = []
	for search_result in search_response.get("items", []):
		if search_result["id"]["kind"] == "youtube#video" :
			videos.append(search_result["id"]["videoId"])
	
	#Use list of video IDs to request statistics, content details or anything about the video
	url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,id,contentDetails,statistics&id="+ ','.join(videos) +"&key="+API_KEY
	json_obj = urllib.request.urlopen(url)
	data = json.load(json_obj)

	#Filter all significant info and place them in a list of strings
	videosInfo = []
	for item in data["items"]:
		videosInfo.append("%s| %s| %s| %s| %s| %s| %s" % (item["snippet"]["title"],
												item["id"],
												item["snippet"]["channelTitle"],
												item["contentDetails"]["duration"],
												item["statistics"]["viewCount"],
												item["statistics"]["commentCount"],
												item["statistics"]["likeCount"]))
	#print("\n".join(videoList))

	#Generate CSV file by using the list VideoInfo
	f = open('./youtube_data.csv', 'w', newline='', encoding='utf-8')
	w = csv.writer(f, delimiter = ',')
	w.writerow(["Title","Video ID","Channel","Duration","View count","Comment count","Like count"])
	w.writerows([x.split('|') for x in videosInfo])
	f.close()


if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="Google")
  argparser.add_argument("--max_results", help="Max results", default=25)
  args = argparser.parse_args()
  try:
    youtubeAPI(args)
  except urllib.error.HTTPError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
  