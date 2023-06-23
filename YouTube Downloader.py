from pytube import YouTube
from pytube import Playlist
from pytube.cli import on_progress
import os
import inquirer
import re
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("Youtube Downloader")
os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.path.dirname(__file__), "certifi", "cacert.pem")
playlist_option = inquirer.prompt([inquirer.List("playlist", message="\033[92m Choose Playlist Option\033[0m", choices=["Create Playlist","Download Playlist",])])

def replace_invalid_characters(title):
    return re.sub(r'[<>:"/\|?*]', '_', title)

def error_video_download(err_video, resolution_option, output_path):
    print(f"\n \033[92m Errors Video Downloading... [{err_video.length}] \033[0m ")
    for videos in err_video:
        video_download(videos[1], videos[0], output_path, resolution_option)

def video_download(url, count, output_path, resolution_option, ext = 'mp4'):
    video = YouTube(url, on_progress_callback=on_progress)
    print(f"\n\n{count}. {video.title}")
    if resolution_option["resolution"] == 'Select Highest Resolution':
        stream_choosed = video.streams.get_highest_resolution()
    elif resolution_option["resolution"] == 'Select Lowest Resolution':
        stream_choosed = video.streams.get_lowest_resolution()
    elif resolution_option["resolution"] == 'Select Only Audio':
        stream_choosed = video.streams.get_audio_only()
        ext='mp3'
    else:
        stream_choosed = video.streams.filter(file_extension='mp4', resolution=resolution_option["resolution"]).first()
        
    if stream_choosed is not None:
        stream = stream_choosed
    else:
        print(f'No {stream_choosed} resolution available for {video.title}')
        return "continue"
    
    file_name = f"{count}. {replace_invalid_characters(video.title)}.{ext}"
    os.path.join(output_path, file_name)
    stream.download(output_path=output_path, filename=file_name)
    print(f"\033[91m Downloaded \033[94m Resolution: {stream_choosed.resolution} \033[92m Size: {stream.filesize_mb:.2f} MB \033[0m")
    return "continue"

if playlist_option['playlist'] == 'Download Playlist':
    errors = []
    start = 0
    playlist = Playlist(input("Enter the URL of the playlist: "))
    res = [inquirer.List("resolution", message="\033[92m Select the Resolution for Videos \033[0m", choices=["Select Highest Resolution","1080p","720p","480p","Select Lowest Resolution","Select Only Audio",])]
    resolution_option = inquirer.prompt(res)
    count = 0
    print(f"\n \033[92m {playlist.title} | {playlist.owner} | Videos {playlist.length} \033[0m ")
    ext='mp4'
    start_option = inquirer.prompt(inquirer.List("Start", message="\033[92m Select the Starting For Download \033[0m", choices=["All", "Custom"]))
    
    if start_option["Start"] == "Custom":
        while True:
            start = int(input(f"Enter starting of video {0}-{playlist.length}: "))
            if start > playlist.length:
                print("Strting should be less than length of playlist")
                continue
            else:
                break

    output_folder_name = f"{playlist.title.replace('|', '')} - {playlist.owner.replace('|', '')}"
    output_path = os.path.join("Download", output_folder_name)
    os.makedirs(output_path, exist_ok=True)

    for url in playlist:
        count += 1
        if count < start:
            continue
        
        try:
            video_download(url, count, output_path, resolution_option)
        except Exception as e:
            print(f'\033[91m{e}\033[0m')
            errors.append([count, url])
        continue

    if errors.length > 0:
        error_video_download(errors, resolution_option, output_path)

    input("\n\n\033[91mPress Enter to Exit\033[0m")
            
elif playlist_option['playlist'] == 'Create Playlist':
    errors = []
    playlist_own = set()
    while True:
        add_to_playlist = inquirer.prompt([inquirer.List("add_to_playlist", message="\033[92m Add More Videos\033[0m", choices=["Yes","No","Show Playlist"])])
        if add_to_playlist['add_to_playlist'] == 'Yes':
            lst = input('\033[92m Enter Video Url: \033[0m')
            playlist_own.add(lst)
        elif add_to_playlist['add_to_playlist'] == 'Show Playlist':
            count = 0
            for data in playlist_own:
                count+=1
                print(f'\033[94m{count}. {data}\033[0m')
            print('\n')
        else:
            break
    
    if len(playlist_own)>0:
        playlist_name = input('Enter the Playlist Name: ')
        output_path = os.path.join("Download", playlist_name)
        os.makedirs(output_path, exist_ok=True)
        res = [inquirer.List("resolution", message="\033[92m Select the Resolution for Videos \033[0m", choices=["Select Highest Resolution","1080p","720p","480p","Select Lowest Resolution","Select Only Audio",])]
        resolution_option = inquirer.prompt(res)
        count = 0
        for url in playlist_own:
            count+=1
            try:
                video_download(url, count, output_path, resolution_option)
            except Exception as e:
                print(f'\033[91m{e}\033[0m')
                errors.append([count, url])
            continue

        if errors.length > 0:
            error_video_download(errors, resolution_option, output_path)

input("\n\n\033[91mPress Enter to Exit\033[0m")