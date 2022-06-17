from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import csv 
import os
import pandas as pd


def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    response = request.execute() 
    
    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscribers = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
    
    return all_data



def get_video_ids(youtube, playlist_id):
    
    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()
    
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
        
    return video_ids



def get_content(contents,count):
    csv_file='content/text_%s.csv'%(str(count))
    csv_columns = ['text','start','duration']
    with open(csv_file, 'w', encoding="utf-8",newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in contents:
            writer.writerow(data)
            
        csvfile.close()
        
        
def write_count(count,path):
    with open(path,'w') as f:
        f.write(str(count))
        f.close()

def get_video_details(youtube, video_ids,count,count1):

    for i in range(0, len(video_ids),50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50]))
        response = request.execute()
        #print(response['items'][0])
        for video in response['items']:
            print('process vid %d %s :'%(count1,video['snippet']['title']))
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video['id'])
                list_language=[x.language for x in transcript_list]
                print(list_language)
                if 'Tiếng Việt' not in list_language:
                    count1+=1
                    write_count(count1,'counter.txt')
                    print('continue')
                    continue
            except(Exception,):
                count1+=1
                write_count(count1,'counter.txt')
                print('continue')
                continue
    
               
            video_stats = [video['snippet']['title'],
                               video['snippet']['publishedAt'],
                            video['statistics']['viewCount'],
                               video['id']
                               ]
            
            if (os.path.exists('index.csv')== False):
                csv_columns = ['Title','Published_date','Views','id']
                with open("index.csv", 'w',newline='') as file:
                    dw = csv.DictWriter(file, delimiter=',', 
                                        fieldnames=csv_columns)
                    dw.writeheader()
                    file.close()
                    
            with open('index.csv', 'a', encoding="utf-8",newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(video_stats)
                csvfile.close()
                
            contents=YouTubeTranscriptApi.get_transcript(video['id'], languages=['vi'])
            get_content(contents,count)
                
            count1+=1
            count+=1
            write_count(count1,'counter.txt')
    print('sucessful !!!!!!!!!!!!!!')