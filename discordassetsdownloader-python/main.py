import requests
import os
import re

def sanitize_filename(filename):
    valid_filename = re.sub(r'[<>:"/\|?*]', '', filename)
    return valid_filename[:255]

def get_unique_filename(directory, filename):
    base_name, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename

    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base_name}-{counter}{extension}"
        counter += 1

    return unique_filename

def download_discord_attachments_from_folder(folder_path, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    url_pattern = re.compile(r'https://(/?:cdn\.discordapp\.com|media\.discordapp\.net)/attachments/\S+')

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            subdirectory_name = os.path.splitext(file_name)[0]
            subdirectory_path = os.path.join(download_folder, sanitize_filename(subdirectory_name))
            if not os.path.exists(subdirectory_path):
                os.makedirs(subdirectory_path)

            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    urls = url_pattern.findall(line)
                    for url in urls:
                        try:
                            file_name = url.split('/')[-1].split('?')[0]
                            sanitized_file_name = sanitize_filename(file_name)
                            unique_file_name = get_unique_filename(subdirectory_path, sanitized_file_name)
                            download_path = os.path.join(subdirectory_path, unique_file_name)

                            response = requests.get(url)
                            response.raise_for_status()

                            with open(download_path, 'wb') as download_file:
                                download_file.write(response.content)
                            print(f'Downloaded: {unique_file_name} from {file_path}')

                        except requests.exceptions.RequestException as e:
                            print(f'Failed to download {url} from {file_path}: {e}')

folder_with_txt_files = '' # Replace with the path to your folder containing text files
download_directory = '' # Replace with your desired download folder
download_discord_attachments_from_folder(folder_with_txt_files, download_directory)
