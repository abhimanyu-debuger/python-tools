from pytubefix import YouTube
from pytubefix.cli import on_progress
import re
import os
import subprocess
import shutil
import sys

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename[:200] if len(filename) > 200 else filename

def check_ffmpeg():
    """Check if FFmpeg is available"""
    # Try multiple methods to find FFmpeg
    try:
        # Method 1: Check if ffmpeg is in PATH
        if shutil.which('ffmpeg') is not None:
            return True
        
        # Method 2: Try running ffmpeg directly
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        if result.returncode == 0:
            return True
    except:
        pass
    
    return False

def merge_video_audio(video_path, audio_path, output_path):
    """Merge video and audio using FFmpeg with multiple fallback methods"""
    
    methods = [
        {
            'name': 'Fast copy',
            'cmd': ['ffmpeg', '-i', video_path, '-i', audio_path, '-c', 'copy', '-y', output_path]
        },
        {
            'name': 'AAC audio encoding',
            'cmd': ['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-y', output_path]
        },
        {
            'name': 'Full re-encode',
            'cmd': ['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac', '-b:a', '192k', '-y', output_path]
        }
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"Attempting merge method {i}/{len(methods)}: {method['name']}...")
            
            result = subprocess.run(
                method['cmd'],
                capture_output=True,
                text=True,
                timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✅ Merge successful using {method['name']}!")
                return True
            else:
                if os.path.exists(output_path):
                    os.remove(output_path)
                print(f"⚠️ Method {i} failed, trying next...")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ Method {i} timed out, trying next...")
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            print(f"⚠️ Method {i} error: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
    
    return False

def download_youtube_video(url, auto_select_best=False, preferred_resolution=None):
    try:
        print("Fetching video...")
        yt = YouTube(url, on_progress_callback=on_progress)
        
        print(f"\nTitle: {yt.title}")
        print(f"Duration: {yt.length // 60}:{yt.length % 60:02d}")
        
        # Check FFmpeg availability
        ffmpeg_available = check_ffmpeg()
        if not ffmpeg_available:
            print("\n⚠️ FFmpeg not detected in system PATH!")
            print("Only resolutions up to 720p will be available.\n")
            print("To enable 1080p+ downloads:")
            print("1. Find your FFmpeg installation (you mentioned it's installed)")
            print("2. Add FFmpeg to your system PATH:")
            print("   - Search 'Environment Variables' in Windows")
            print("   - Edit 'Path' variable")
            print("   - Add the FFmpeg 'bin' folder path (e.g., C:\\ffmpeg\\bin)")
            print("   - Restart your terminal/Jupyter notebook")
            print("\nOR provide the full path to ffmpeg.exe in the code\n")
        else:
            print("✅ FFmpeg detected - High quality downloads available\n")
        
        # Get all video streams
        all_streams = []
        
        # Progressive streams (video + audio combined, usually up to 720p)
        progressive = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        for stream in progressive:
            all_streams.append({
                'stream': stream,
                'resolution': stream.resolution,
                'type': 'progressive',
                'filesize': stream.filesize,
                'video_stream': None,
                'audio_stream': None
            })
        
        # Adaptive streams (video only, includes 1080p, 1440p, 4K) - only if FFmpeg available
        if ffmpeg_available:
            adaptive = yt.streams.filter(adaptive=True, only_video=True, file_extension='mp4').order_by('resolution').desc()
            for stream in adaptive:
                # Skip if we already have this resolution in progressive
                if not any(s['resolution'] == stream.resolution for s in all_streams):
                    # Get best audio stream
                    audio = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
                    all_streams.append({
                        'stream': stream,
                        'resolution': stream.resolution,
                        'type': 'adaptive',
                        'filesize': stream.filesize + (audio.filesize if audio else 0),
                        'video_stream': stream,
                        'audio_stream': audio
                    })
        
        # Sort by resolution (highest first)
        all_streams.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)
        
        if not all_streams:
            print("❌ No available streams found!")
            return
        
        # Auto-select resolution
        selected = None
        
        if auto_select_best:
            selected = all_streams[0]
            print(f"Auto-selected highest quality: {selected['resolution']}")
        elif preferred_resolution:
            for item in all_streams:
                if item['resolution'] == preferred_resolution:
                    selected = item
                    print(f"Selected: {preferred_resolution}")
                    break
            
            if not selected:
                print(f"⚠️ {preferred_resolution} not available, using highest quality instead")
                selected = all_streams[0]
        else:
            # Display available resolutions with better formatting
            print("\n" + "="*70)
            print("AVAILABLE RESOLUTIONS")
            print("="*70)
            print(f"{'#':<4} {'Resolution':<12} {'Size':<12} {'Type':<20}")
            print("-"*70)
            
            for i, item in enumerate(all_streams, 1):
                size_mb = item['filesize'] / (1024 * 1024)
                stream_type = "✓ Ready (with audio)" if item['type'] == 'progressive' else "⚡ High Quality (needs merge)"
                print(f"{i:<4} {item['resolution']:<12} {size_mb:>6.1f} MB    {stream_type}")
            
            print("="*70)
            
            # Let user choose
            while True:
                try:
                    choice = input(f"\n👉 Select resolution [1-{len(all_streams)}] or press Enter for best quality: ").strip()
                    
                    if choice == "":
                        selected = all_streams[0]
                        print(f"✅ Selected: {selected['resolution']} (highest quality)")
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(all_streams):
                        selected = all_streams[choice_num - 1]
                        print(f"✅ Selected: {selected['resolution']}")
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(all_streams)}")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
                except KeyboardInterrupt:
                    print("\n\n❌ Download cancelled by user")
                    return
        
        # Clean filename
        filename = sanitize_filename(yt.title) + ".mp4"
        
        print(f"\n{'='*70}")
        print(f"DOWNLOAD STARTING")
        print(f"{'='*70}")
        print(f"File: {filename}")
        print(f"Quality: {selected['resolution']}")
        print(f"Size: {selected['filesize'] / (1024 * 1024):.1f} MB")
        print(f"{'='*70}\n")
        
        if selected['type'] == 'progressive':
            # Simple download (video + audio already combined)
            print("Downloading...")
            selected['stream'].download(filename=filename)
        else:
            # Download video and audio separately, then merge with FFmpeg
            video_path = "temp_video.mp4"
            audio_path = "temp_audio.mp4"
            
            try:
                print("Downloading video...")
                selected['video_stream'].download(filename=video_path)
                
                print("\nDownloading audio...")
                selected['audio_stream'].download(filename=audio_path)
                
                print("\nMerging video and audio...")
                
                if merge_video_audio(video_path, audio_path, filename):
                    # Clean up temp files
                    os.remove(video_path)
                    os.remove(audio_path)
                else:
                    raise Exception("All merge methods failed")
                    
            except Exception as e:
                print(f"\n❌ Error during download/merge: {e}")
                
                # Clean up temp files
                for temp_file in [video_path, audio_path]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                
                # Try fallback to progressive stream
                print("\nAttempting fallback to lower quality with audio...")
                fallback = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if fallback:
                    print(f"Downloading {fallback.resolution}...")
                    fallback.download(filename=filename)
                else:
                    print("❌ No fallback stream available")
                    return
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename) / (1024 * 1024)
            print(f"\n{'='*70}")
            print(f"✅ DOWNLOAD COMPLETE!")
            print(f"{'='*70}")
            print(f"File: {filename}")
            print(f"Size: {file_size:.1f} MB")
            print(f"Location: {os.path.abspath(filename)}")
            print(f"{'='*70}")
        else:
            print("\n❌ Download failed - file not found")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*70)
    print(" "*20 + "YOUTUBE VIDEO DOWNLOADER")
    print("="*70)
    
    # OPTIONAL: If FFmpeg is not in PATH, specify the full path here
    # Example: FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
    FFMPEG_PATH = r"C:\Users\abhimanyu.banerjee\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe"
    
    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        # Override system FFmpeg with custom path
        os.environ['PATH'] = os.path.dirname(FFMPEG_PATH) + os.pathsep + os.environ['PATH']
        print(f"✅ Using custom FFmpeg path: {FFMPEG_PATH}\n")
    
    video_url = input("\n📺 Enter YouTube URL: ").strip()
    
    # Configuration options:
    # Set AUTO_SELECT_BEST to True to automatically download highest quality
    # Set PREFERRED_RESOLUTION to specific resolution like '1080p', '720p', etc.
    # Leave both as shown below to get interactive resolution selection
    
    AUTO_SELECT_BEST = False     # Change to True to skip resolution selection
    PREFERRED_RESOLUTION = None   # Or set to '1080p', '720p', '360p' etc.
    
    download_youtube_video(
        url=video_url,
        auto_select_best=AUTO_SELECT_BEST,
        preferred_resolution=PREFERRED_RESOLUTION
    )