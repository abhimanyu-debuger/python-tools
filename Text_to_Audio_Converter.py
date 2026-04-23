import asyncio
import edge_tts
import os

# ============================================================
# 🎯 EDIT THESE SETTINGS BELOW:
# ============================================================

# 1. Choose voice (1-6):
VOICE_CHOICE = "5"

# 2. Enter filename (without .mp3):
OUTPUT_FILENAME = "1A2A3"

# 3. Enter your narration text:
NARRATION_TEXT = """
Once the scheduled length is completed, the self-propelled portal cranes are loaded back onto the BFRs and the entire rake is moved out, leaving behind a modern, renewed track.
"""

# ============================================================
# Don't edit below this line
# ============================================================

output_dir = "narrations"
os.makedirs(output_dir, exist_ok=True)

VOICES = {
    "1": ("en-US-GuyNeural", "American Male (Professional)"),
    "2": ("en-US-JennyNeural", "American Female (Professional)"),
    "3": ("en-GB-RyanNeural", "British Male (Documentary)"),
    "4": ("en-GB-SoniaNeural", "British Female (Documentary)"),
    "5": ("en-IN-PrabhatNeural", "Indian Male (Clear)"),
    "6": ("en-IN-NeerjaNeural", "Indian Female (Clear)"),
}

async def generate_narration():
    """Generate professional narration MP3"""
    
    print("=" * 60)
    print("🎙️  PROFESSIONAL NARRATION GENERATOR")
    print("    by Abhimanyu Banerjee")
    print("=" * 60)
    
    # Validate voice
    voice_choice = VOICE_CHOICE
    if voice_choice not in VOICES:
        print(f"⚠️  Invalid voice '{voice_choice}', using default (1)")
        voice_choice = "1"
    
    selected_voice, voice_name = VOICES[voice_choice]
    print(f"\n📢 Voice: {voice_name}")
    
    # Validate text
    text = NARRATION_TEXT.strip()
    if not text:
        print("\n❌ Error: No text provided!")
        print("Please edit NARRATION_TEXT at the top of the code.")
        return None
    
    print(f"📝 Text: {len(text)} characters, {len(text.split())} words")
    
    # Prepare filename
    filename = OUTPUT_FILENAME
    if not filename.endswith('.mp3'):
        filename += '.mp3'
    
    full_path = os.path.join(output_dir, filename)
    
    # Auto-rename if exists
    counter = 1
    original_name = filename
    while os.path.exists(full_path):
        name, ext = os.path.splitext(original_name)
        filename = f"{name}_{counter}{ext}"
        full_path = os.path.join(output_dir, filename)
        counter += 1
    
    print(f"💾 Filename: {filename}")
    
    # Generate
    print("\n🎬 GENERATING NARRATION...")
    print("-" * 60)
    
    try:
        # Professional narration settings
        communicate = edge_tts.Communicate(text, selected_voice, rate="+0%", pitch="+0Hz")
        await communicate.save(full_path)
        
        print("\n✅ SUCCESS!")
        print(f"📁 File: {os.path.basename(full_path)}")
        print(f"📂 Location: {output_dir}/")
        file_size = os.path.getsize(full_path) / 1024
        print(f"📊 Size: {file_size:.1f} KB")
        print("=" * 60)
        
        return full_path
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# Apply nest_asyncio for Jupyter
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'nest_asyncio'])
    import nest_asyncio
    nest_asyncio.apply()

# Run
asyncio.run(generate_narration())

print("\n💡 VOICE OPTIONS:")
print("  1 = American Male (Professional)")
print("  2 = American Female (Professional)")
print("  3 = British Male (Documentary)")
print("  4 = British Female (Documentary)")
print("  5 = Indian Male (Clear)")
print("  6 = Indian Female (Clear)")
print("\n📝 To create another narration:")
print("   1. Edit VOICE_CHOICE, OUTPUT_FILENAME, and NARRATION_TEXT at the top")
print("   2. Run the cell again")