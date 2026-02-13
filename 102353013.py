import sys
import os
import time
import glob
import traceback
from yt_dlp import YoutubeDL
try:
    # Try importing from moviepy (v2.x)
    from moviepy import AudioFileClip, concatenate_audioclips
except ImportError:
    # Fallback to moviepy.editor (v1.x)
    try:
        from moviepy.editor import AudioFileClip, concatenate_audioclips
    except ImportError:
        print("Error: moviepy not installed or incompatible version.")
        sys.exit(1)

import imageio_ffmpeg

def download_audio(singer, n):
    """Downloads n audio files of the singer from YouTube."""
    # Query optimization: "song" often returns individual tracks compared to "audio" (which returns full albums)
    query = f"{singer} song"
    output_template = "temp_audio/%(title)s.%(ext)s"
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Check for cookies.txt
    cookies_path = "cookies.txt"
    if not os.path.exists(cookies_path):
        # Fallback to an environment variable if provided (for deployment)
        if os.environ.get("YOUTUBE_COOKIES"):
            with open(cookies_path, "w") as f:
                f.write(os.environ.get("YOUTUBE_COOKIES"))
        else:
            cookies_path = None
    
    if cookies_path:
        print(f"DEBUG: Using cookies from {cookies_path}")
    else:
        print("DEBUG: No cookies found. YouTube might block requests.")

    # Phase 1: Search and filter
    print(f"Searching for short videos of {singer}...")
    search_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
        'cookiefile': cookies_path,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    }
    
    valid_urls = []
    with YoutubeDL(search_opts) as ydl:
        try:
            # Search for 10x the required amount to find enough short videos
            # Compilations are very common, so we need a wide net.
            search_query = f"ytsearch{n*10}:{query}"
            print(f"DEBUG: Searching with query: {search_query}")
            result = ydl.extract_info(search_query, download=False)
            
            if 'entries' in result:
                for entry in result['entries']:
                    # entries might be None if failed
                    if not entry: continue
                    
                    title = entry.get('title', 'Unknown')
                    duration = entry.get('duration')
                    url = entry.get('url')
                    print(f"DEBUG: Found video: {title} ({duration}s)")
                    
                    # If duration is None, we can't filter, so maybe skip or risk it? 
                    # Let's skip safely.
                    if duration and duration < 600: # < 10 mins
                        valid_urls.append(url)
                        print(f"DEBUG: Added {title}")
                        if len(valid_urls) >= n:
                            break
                    else:
                        print(f"DEBUG: Skipped {title} (too long)")
            else:
                print("DEBUG: No entries in result")
        except Exception as e:
            print(f"Error during search: {e}")

    if not valid_urls:
        print("No videos found matching criteria.")
        return

    print(f"Found {len(valid_urls)} valid short videos. Downloading...")

    # Phase 2: Download
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': output_template,
        'quiet': False,
        'ignoreerrors': True,
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': cookies_path,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
             ydl.download(valid_urls)
        except Exception as e:
            print(f"Error during download: {e}")

def process_audio(duration, output_file):
    """Trims and merges audio files. Returns True if successful, False otherwise."""
    audio_files = glob.glob("temp_audio/*.mp3")
    
    if not audio_files:
        print("No audio files found downloaded.")
        return False

    print(f"Found {len(audio_files)} files. Processing...")
    
    clips = []
    for file in audio_files:
        try:
            clip = AudioFileClip(file)
            # Trim
            subclip = clip.subclipped(0, duration)
            clips.append(subclip)
        except Exception as e:
            print(f"Skipping {file}: {e}")
            traceback.print_exc()
            continue

    if not clips:
        print("No valid clips created.")
        return False

    print(f"Merging {len(clips)} clips...")
    try:
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(output_file)
        final_clip.close()
    except Exception as e:
        print(f"Error merging clips: {e}")
        traceback.print_exc()
        return False
    
    # Close source clips
    for clip in clips:
        clip.close()
    
    return True

def cleanup():
    """Removes temporary files."""
    files = glob.glob("temp_audio/*")
    for f in files:
        try:
            os.remove(f)
        except:
            pass
    try:
        os.rmdir("temp_audio")
    except:
        pass

def main():
    if len(sys.argv) != 5:
        print("Usage: python 102353013.py <SingerName> <NumberOfVideos> <DurationEach> <OutputFileName>")
        sys.exit(1)

    singer = sys.argv[1]
    
    try:
        n_videos = int(sys.argv[2])
        duration = int(sys.argv[3])
    except ValueError:
        print("NumberOfVideos and DurationEach must be integers.")
        sys.exit(1)
        
    output_file = sys.argv[4]
    
    if n_videos <= 0:
        print("NumberOfVideos must be greater than 0")
        sys.exit(1)

    if duration <= 0:
        print("DurationEach must be greater than 0")
        sys.exit(1)
        
    if not output_file.endswith('.mp3'):
         output_file += '.mp3'

    # Create temp directory
    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")
        
    try:
        download_audio(singer, n_videos)
        success = process_audio(duration, output_file)
        if success:
            print(f"Mashup created successfully: {output_file}")
        else:
            print("Mashup creation failed: No audio processed.")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        cleanup()

if __name__ == "__main__":
    main()
