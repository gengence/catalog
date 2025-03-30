import json
import os
import threading 
import time
import websocket
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKENS_ENV')
GATEWAY = os.getenv('GATEWAY_ENV')
CHANNEL_IDS = os.getenv('CHANNEL_IDS_ENV').split(',')


PAYLOAD = {
    "op": 2,
    "d": {
        "token": TOKEN,
        "properties": {
            "os": 'Windows',
            "browser": 'Chrome',
            "device": 'PC'
        }
    }
}

HEARTBEATPAYLOAD = {
    "op": 1,
    "d": 'null' 
}


def json_request(ws, request):
    ws.send(json.dumps(request))

def json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(rythm, ws):
    while True:
        time.sleep(rythm)
        try:
            json_request(ws, HEARTBEATPAYLOAD)
        except websocket.WebSocketConnectionClosedException:
            print("Heartbeat Failed: WebSocket Connection Closed.")
            break

def get_username():
    ws = websocket.WebSocket()
    ws.connect(GATEWAY)

    json_request(ws, PAYLOAD)

    while True:
        event = json_response(ws)
        if 'd' in event and 'user' in event['d']:
            ws.close()
            return event['d']['user']['username']

def log_message(username_folder, channel_id, guild_id, message):
    if str(channel_id) in CHANNEL_IDS:
        filename = os.path.join(username_folder, f'{channel_id}.txt')
    elif guild_id is None:
        filename = os.path.join(username_folder, 'DMS.txt')
    else:
        filename = os.path.join(username_folder, 'SERVERS.txt')
    with open(filename, 'a', encoding='utf-8') as logs:
        logs.write(f'{message}\n')

def log_update(username_folder, message):
    filename = os.path.join(username_folder, 'UPDATES.txt')
    with open(filename, 'a', encoding='utf-8') as logs:
        logs.write(f'{message}\n')

def message_handler(event, username_folder):
    author = event.get('author', {}).get('username')
    content = event.get('content', '')
    attachments = event.get('attachments', [])
    channel_id = event.get('channel_id')
    guild_id = event.get('guild_id') 

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if guild_id is None:
        location = f"DM sent in Channel {channel_id}"
    else:
        location = f"Server {guild_id}, Channel {channel_id}"

    if not attachments:
        message = f'{timestamp} - {author} ({location}): {content}'

    else:
        attachment_urls = '\n'.join([attachment['url'] for attachment in attachments])
        message = f'{timestamp} - {author} ({location}): {content}\n{attachment_urls}'
    
    log_message(username_folder, channel_id, guild_id, message)

def voice_handler(event, username_folder):
    user = event['member']['user']['username']
    channel_id = event.get('channel_id')
    guild_id = event.get('guild_id')
    video = event.get('self_video')
    stream = event.get('self_stream')
    mute = event.get('self_mute')
    deaf = event.get('self_deaf')

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if channel_id == None:
        message = f'{timestamp} - {user} left the Voice Channel.'
    else:
        message = f'{timestamp} - {user} Voice State updated in {channel_id}. Video: {str(video)}. Stream: {str(stream)}. Muted: {str(mute)}. Deafened: {str(deaf)}.'

    log_message(username_folder, channel_id, guild_id, message)

def update_handler(event, username_folder, username):
    status = event['status']

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f'{timestamp} - {username} updated their status to {status}.'
    log_update(username_folder, message)
                   
def animate(username_folder, username):
    while True:
        try:
            ws = websocket.WebSocket()
            ws.connect(GATEWAY)

            event = json_response(ws)
            rythm = event['d']['heartbeat_interval'] / 1000

            threading._start_new_thread(heartbeat, (rythm, ws))
            json_request(ws, PAYLOAD)

            while True:
                event = json_response(ws)

                try:
                    if 'd' not in event:
                        continue

                    event_type = event.get('t')
                    op_code = event.get('op')

                    if event_type == 'MESSAGE_CREATE':
                        message_handler(event['d'], username_folder)
                    elif event_type == 'VOICE_STATE_UPDATE':
                        voice_handler(event['d'], username_folder)
                    elif event_type == 'USER_SETTINGS_UPDATE':
                        update_handler(event['d'], username_folder, username)

                    
                    if op_code == 11:
                        print("Heartbeat Acknowledged...")

                except:
                    pass

        except websocket.WebSocketConnectionClosedException:
            print('WebSocket Connection Closed, Attempting To Reconnect...')


def main():
    username = get_username()
    username_folder = os.path.join(os.getcwd(), username)
    os.makedirs(username_folder, exist_ok=True)
    animate(username_folder, username)

if __name__ == '__main__':
    main()