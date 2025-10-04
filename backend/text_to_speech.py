# To run this code you need to install the following dependencies:
# pip install elevenlabs python-dotenv

import os
from elevenlabs import generate, play, set_api_key
from dotenv import load_dotenv
from typing import Optional



load_dotenv()

def text_to_speech(text: str, voice_id: Optional[str] = None, output_file: str = "output.mp3") -> str:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text: The text to convert to speech
        voice_id: ElevenLabs voice ID (optional, uses default voice if None)
        output_file: Path where to save the audio file
        
    Returns:
        str: Path to the generated audio file
        
    Raises:
        ValueError: If ELEVENLABS_API_KEY is not set
        Exception: If API call fails
    """
    # Get API key from environment
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY must be set in environment variables")
    
    # Set the API key
    set_api_key(api_key)
    
    # Set default voice if none provided
    if voice_id is None:
        # This is a popular voice ID from ElevenLabs (Rachel)
        voice_id = "21m00Tcm4TlvDq8ikWAM"
    
    try:
        # Generate audio from text
        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        # Save audio to file
        with open(output_file, "wb") as f:
            f.write(audio)
        
        print(f"Audio saved to: {output_file}")
        return output_file
        
    except Exception as e:
        raise Exception(f"Failed to generate speech: {str(e)}")


def play_text_to_speech(text: str, voice_id: Optional[str] = None, auto_play: bool = True) -> str:
    """
    Convert text to speech and optionally play it immediately.
    
    Args:
        text: The text to convert to speech
        voice_id: ElevenLabs voice ID (optional)
        auto_play: Whether to automatically play the audio after generation
        
    Returns:
        str: Path to the generated audio file
    """
    import tempfile
    import os
    import subprocess
    import platform
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        temp_audio_file = tmp_file.name
    
    try:
        # Generate speech
        audio_file = text_to_speech(text, voice_id, temp_audio_file)
        
        # Play audio if requested
        if auto_play:
            system = platform.system()
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(["afplay", audio_file], check=True)
                elif system == "Windows":
                    os.startfile(audio_file)
                elif system == "Linux":
                    subprocess.run(["aplay", audio_file], check=True)
                else:
                    print(f"Auto-play not supported on {system}. Audio saved to: {audio_file}")
            except subprocess.CalledProcessError:
                print(f"Could not auto-play audio. File saved to: {audio_file}")
        
        return audio_file
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_audio_file):
            os.unlink(temp_audio_file)
        raise e


# Example usage and testing
if __name__ == "__main__":
    try:
        # Example 1: Basic text to speech
        sample_text = "Hello! This is a test of the ElevenLabs text to speech conversion."
        audio_file = text_to_speech(sample_text, output_file="test_speech.mp3")
        print(f"Basic TTS completed: {audio_file}")
        
        # Example 2: Text to speech with auto-play
        sample_text2 = "This audio will play automatically after generation."
        audio_file2 = play_text_to_speech(sample_text2, auto_play=True)
        print(f"Auto-play TTS completed: {audio_file2}")
        
        # Example 3: Using different voice
        # You can get voice IDs from ElevenLabs dashboard
        sample_text3 = "This uses a specific voice ID."
        custom_voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella voice
        audio_file3 = text_to_speech(sample_text3, voice_id=custom_voice_id, output_file="custom_voice.mp3")
        print(f"Custom voice TTS completed: {audio_file3}")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure to set ELEVENLABS_API_KEY in your .env file")
    except Exception as e:
        print(f"Error: {e}")
