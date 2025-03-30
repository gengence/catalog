import sys
import os
import yt_dlp

def download(channel_name):
    output_dir = f'{channel_name}'
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'best',
        'quiet': False,
        'extract_flat': False,
        'playlistreverse': True,
        'ignoreerrors': True,
    }
    
    url = f'https://www.twitch.tv/{channel_name}/clips?filter=clips&range=all'
    
    print(f"Downloading all clips from {channel_name}...")
    print("This may take a while depending on how many clips exist...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"\nClips have been downloaded to: {output_dir}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <channel_name>")
        sys.exit(1)
        
    channel_name = sys.argv[1]
    download(channel_name) 