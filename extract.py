import json
import os
import subprocess

from dotenv import load_dotenv


def extract_urls(json_file):
    video_urls = []
    with open(json_file, 'r') as file:
        for line in file:
            video_info = json.loads(line)
            if "url" in video_info:
                url = video_info["url"]
                # Ensure the URL is correct (avoid double prefix)
                if url.startswith("http"):
                    video_urls.append(url)
                else:
                    video_urls.append(f"https://www.tiktok.com/{url.lstrip('/')}")
    return video_urls


def main():
    # ensure ffmeg is installed, if not exit with message to user.
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        print("ffmpeg is not installed. Please install ffmpeg before running this script.")
        return


    # Load settings.cfg into the os environment
    load_dotenv("settings.cfg")

    collection_url = os.getenv("COLLECTION_URL")
    collection_name = os.getenv("COLLECTION_NAME")
    output_path = os.getenv("OUTPUT_PATH")
    
    if not collection_url:
        print("COLLECTION_URL is not set in settings.cfg")
        return

    if not collection_name:
        print("COLLECTION_NAME is not set in settings.cfg")
        return

    if not output_path: 
        print("OUTPUT_PATH is not set in settings.cfg")
        return
    else:
        # validate that the path exists
        if not os.path.exists(output_path):
            print("OUTPUT_PATH does not exist on your system, please create the directory first.")
            return

    collection_directory = os.path.join(output_path, collection_name)
    # Ensure the output path exists
    os.makedirs(collection_directory, exist_ok=True)

    # File paths
    json_file = os.path.join(output_path, collection_name, f"{collection_name}_urls.json")
    urls_file = os.path.join(output_path, collection_name, f"{collection_name}_videos.txt")

    # Run yt-dlp to fetch video URLs and save to JSON
    print(f"Extracting video URLs for {collection_name}... this may take a moment.")
    subprocess.run([
        'yt-dlp', '--flat-playlist', collection_url, '-j'
    ], stdout=open(json_file, 'w'), check=True)

    # Extract URLs from the JSON file
    video_urls = extract_urls(json_file)

    # Save extracted URLs to a text file
    with open(urls_file, "w") as file:
        for url in video_urls:
            file.write(url + "\n")

    print(f"Extracted {len(video_urls)} video URLs. Saved to {urls_file}\n")
    print(f"To scrape videos, copy and paste the following command: \n\n   yt-dlp -f \"bv*+ba/b\" -a '{urls_file}' -o '{collection_directory}/TikTok_%(uploader).50s_%(title).50s_%(like_count)dlikes.%(ext)s'")
    print("\nNote: The above command will download videos to the output path.")


# entry point for the script
if __name__ == "__main__":
    main()
