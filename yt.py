import os
import random
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from youtubesearchpython import *
import spintax
import time
from datetime import datetime, timedelta

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl',
          'https://www.googleapis.com/auth/youtubepartner'
          ]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def pick_video():
  with open(r'data/keywords.txt', 'r') as f:
    keywords = [line.strip() for line in f]
    random_keyword = random.choice(keywords)
    keys = spintax.spin(random_keyword)
    #print(keys)
      
  customSearch = CustomSearch(keys, 'CAMSAggB', limit = 10)
  i = random.randint(0,9)
  viewcount = customSearch.result()['result'][i]['viewCount']['text']
  video_link = customSearch.result()['result'][i]['link']
  video = Video.get(video_link, mode = ResultMode.json, get_upload_date=True)
  print(video_link)
  viewcount_str = str(viewcount).split(' ')[0]
  if len(viewcount_str) > 3:
    video_id = customSearch.result()['result'][i]['id']
    return video_id,video['isFamilySafe']
  else:
    return None,False

def random_video():
  with open(r'data/keywords_common.txt', 'r') as f:
    keywords = [line.strip() for line in f]
    random_keyword = random.choice(keywords)
    keys = spintax.spin(random_keyword)
  video_search = VideosSearch(keys, limit = 20)
  i = random.randint(0,19)
  video_id = video_search.result()['result'][i]['id']
  return video_id

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

  #service = create_service(CLIENT_SECRETS_FILE, API_SERVICE_NAME, API_VERSION, SCOPES)
  #return service

def comment_threads_insert(video_id, service, rand):
  request_body = {
    'snippet': {
      'videoId': video_id,
      'topLevelComment': {
        'snippet': {
          'textOriginal': rand
        }
      }
    }
  }
  response = service.commentThreads().insert(
    part='snippet',
    body=request_body
  ).execute()
  return response

if __name__ == '__main__':
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  global service
  service = get_authenticated_service()

with open(r'data/comments.txt', 'r') as f:
    foo = [line.strip() for line in f]

while True:    
  #scrape(line)        
  video_id,isFamilySafe = pick_video()
  rand = random.choice(foo) 
  if video_id is not None and isFamilySafe:
    try:
      response = comment_threads_insert(video_id, service, rand)
      print(response)      
      print("Comment Success!")      
    except:
      print("Comment Failed!")
      pass
    
    time.sleep(10)
    common_video_id = random_video()
    try:
      response = comment_threads_insert(common_video_id, service, rand)       
      print("Second Comment Success!")      
    except:
      print("Second Comment Failed!")
      pass
    
    dt = datetime.now() + timedelta(hours=1)
    while datetime.now() < dt:
      time.sleep(1)
      
  else:
    pass
  
  