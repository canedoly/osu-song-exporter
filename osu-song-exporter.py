import os
import re
import shutil
import subprocess
import sys

# Configuration
SOURCE_DIR = " " # osu! Songs directory
TARGET_DIR = " " # output directory
EXCLUDED_PREFIXES = ['soft-', 'drum-', 'normal-']

CONVERT_TO_MP3 = True      # 'False' if you want to keep original extensions
HIDE_FFMPEG_WINDOW = True  # 'False' if you want to show ffmpeg window
BITRATE = "192k"           # Only used when CONVERT_TO_MP3 is True

ALLOWED_EXTENSIONS = {'.mp3', '.ogg'}

def clean_folder_name(original_name):
    """Clean folder name by removing beatmap ID and [no video] tags"""
    name = re.sub(r'^\d+\s*', '', original_name)
    name = re.sub(r'\s*\[no\s*video\]\s*', ' ', name, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', name).strip()

def convert_to_mp3(source_path, target_path):
    """Convert audio to MP3 using ffmpeg with window control"""
    try:
        kwargs = {}
        if HIDE_FFMPEG_WINDOW:
            # Window hiding parameters for different platforms
            if sys.platform == 'win32':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            kwargs.update({
                'stdout': subprocess.DEVNULL,
                'stderr': subprocess.DEVNULL
            })

        subprocess.run([
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'error',
            '-y',
            '-i', source_path,
            '-codec:a', 'libmp3lame',
            '-b:a', BITRATE,
            '-vn',
            target_path
        ], check=True, **kwargs)
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {os.path.basename(source_path)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    for folder_name in os.listdir(SOURCE_DIR):
        folder_path = os.path.join(SOURCE_DIR, folder_name)
        
        if not os.path.isdir(folder_path):
            continue

        clean_name = clean_folder_name(folder_name)

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if not os.path.isfile(file_path):
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue
            
            lower_filename = filename.lower()
            if any(lower_filename.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
                continue

            target_ext = '.mp3' if CONVERT_TO_MP3 else ext
            target_filename = f"{clean_name}{target_ext}"
            target_path = os.path.join(TARGET_DIR, target_filename)

            if os.path.exists(target_path):
                continue

            success = False
            if CONVERT_TO_MP3:
                success = convert_to_mp3(file_path, target_path)
            else:
                try:
                    shutil.copy2(file_path, target_path)
                    success = True
                except Exception as e:
                    print(f"Copy failed: {filename}")

            if success:
                action = "Converted" if CONVERT_TO_MP3 else "Copied"
                print(f"{action}: {filename.ljust(40)} -> {target_filename}")
                break  # Process only first valid audio file

if __name__ == "__main__":
    main()
