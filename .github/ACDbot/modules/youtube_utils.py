from googleapiclient.discovery import build
import os
from datetime import datetime, timedelta
import pytz

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def get_channel_id_by_custom_url(custom_url):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    response = youtube.channels().list(
        part='id',
        forUsername=custom_url
    ).execute()

    items = response.get('items', [])
    if items:
        return items[0]['id']
    else:
        # Try retrieving by channel custom URL path
        response = youtube.search().list(
            part='snippet',
            q=custom_url,
            type='channel',
            maxResults=1
        ).execute()
        items = response.get('items', [])
        if items:
            return items[0]['snippet']['channelId']
        else:
            raise Exception("Channel not found")

def get_channel_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    videos = []
    next_page_token = None

    while True:
        res = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token,
            order='date',
            type='video'
        ).execute()

        videos.extend(res['items'])
        next_page_token = res.get('nextPageToken')

        if not next_page_token:
            break

    return videos

def create_youtube_stream(title, description, start_time, privacy_status='public'):
    """
    Creates a YouTube live stream event
    Args:
        title: Stream title
        description: Stream description
        start_time: Start time in ISO format
        privacy_status: public, private, or unlisted
    Returns:
        Dictionary containing stream_id and stream_url
    """
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    # Create the broadcast
    broadcast_insert_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "scheduledStartTime": start_time,
                "description": description,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            }
        }
    ).execute()

    broadcast_id = broadcast_insert_response["id"]

    # Create the stream
    stream_insert_response = youtube.liveStreams().insert(
        part="snippet,cdn",
        body={
            "snippet": {
                "title": title,
            },
            "cdn": {
                "frameRate": "variable",
                "ingestionType": "rtmp",
                "resolution": "variable"
            }
        }
    ).execute()

    stream_id = stream_insert_response["id"]

    # Bind the broadcast to the stream
    youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()

    return {
        "broadcast_id": broadcast_id,
        "stream_id": stream_id,
        "stream_url": f"https://youtube.com/watch?v={broadcast_id}"
    }

def create_recurring_streams(title, description, start_time, occurrence_rate, num_events=4):
    """
    Creates multiple YouTube live stream events for recurring meetings
    Args:
        title: Base title for streams
        description: Stream description
        start_time: Initial start time in ISO format
        occurrence_rate: weekly, bi-weekly, or monthly
        num_events: Number of future events to create
    Returns:
        List of dictionaries containing stream details
    """
    streams = []
    current_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    
    for i in range(num_events):
        # Calculate next event time based on occurrence rate
        if i > 0:
            if occurrence_rate == 'weekly':
                current_time += timedelta(days=7)
            elif occurrence_rate == 'bi-weekly':
                current_time += timedelta(days=14)
            elif occurrence_rate == 'monthly':
                # Add roughly a month (considering variable month lengths)
                if current_time.month == 12:
                    current_time = current_time.replace(year=current_time.year + 1, month=1)
                else:
                    current_time = current_time.replace(month=current_time.month + 1)
        
        event_title = f"{title} #{i+1}"
        stream_details = create_youtube_stream(
            event_title,
            description,
            current_time.isoformat() + 'Z'
        )
        streams.append(stream_details)
    
    return streams

def get_live_streams(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    live_streams = []
    next_page_token = None

    while True:
        res = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='live',
            type='video',
            order='date',
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        live_streams.extend(res['items'])
        next_page_token = res.get('nextPageToken')

        if not next_page_token:
            break

    return live_streams

if __name__ == "__main__":
    custom_url = "EthereumProtocol"
    channel_id = get_channel_id_by_custom_url(custom_url)
    print(f"Channel ID: {channel_id}")

    videos = get_channel_videos(channel_id)
    print("Videos:")
    for video in videos:
        video_id = video['id']['videoId']
        title = video['snippet']['title']
        print(f"{title}: https://www.youtube.com/watch?v={video_id}")

    live_streams = get_live_streams(channel_id)
    print("\nLive Streams:")
    for stream in live_streams:
        stream_id = stream['id']['videoId']
        title = stream['snippet']['title']
        print(f"{title}: https://www.youtube.com/watch?v={stream_id}") 