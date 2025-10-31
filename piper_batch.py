import subprocess
import os
import sys

# ====================================================================
# --- CONFIGURATION (Adjust these values) ---
# ====================================================================

INPUT_FILE = "voice_lines.csv"
OUTPUT_DIR = "PiperTTS_output"
VOICE_MODEL_NAME = "voice_model"
DELIMITER = ";"  # Separator for ID;Text in your CSV

# AUDIO SETTINGS
PIPER_VOLUME = "1.5"  # Volume multiplier (Piper's internal volume)

# --- FFmpeg SPEED CONTROL ---
# This adjusts the playback speed of the generated audio.
# 1.0 = Normal Speed
FFMPEG_SPEED_MULTIPLIER = "1"

ENABLE_POST_PROCESSING = True  # Set to True to enable FFmpeg filters (Recommended)

# FFmpeg Filter Chain
# 1. pan=stereo...: Converts Mono input to Stereo output.
# 2. loudnorm: Normalizes to LUFS (integrated loudness) with a true peak ceiling of -1.0 dB.
FFMPEG_AUDIO_FILTERS = "pan=stereo|c0=c0|c1=c0,loudnorm=I=-10:TP=-1.0:LRA=11"

# ====================================================================
# --- END CONFIGURATION ---\
# ====================================================================

# Construct paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PIPER_EXE = os.path.join(SCRIPT_DIR, "piper.exe")
MODEL_PATH = os.path.join(SCRIPT_DIR, f"{VOICE_MODEL_NAME}.onnx")
VOICE_MODEL_CONFIG = os.path.join(SCRIPT_DIR, f"{VOICE_MODEL_NAME}.onnx.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_DIR)

INPUT_FILE_PATH = os.path.join(SCRIPT_DIR, INPUT_FILE)
TEMP_WAV_FILE = os.path.join(OUTPUT_PATH, "temp_output.wav")


def run_synthesis(line_id, text):
    """
    Runs Piper synthesis and then an optional FFmpeg post-processing step.
    """
    final_output_path = os.path.join(OUTPUT_PATH, f"{line_id}.wav")

    # --- 1. Piper Synthesis Command (outputs to temp file) ---
    piper_command = [
        PIPER_EXE,
        "-m", MODEL_PATH,
        "-c", VOICE_MODEL_CONFIG,
        "--output_file", TEMP_WAV_FILE,
        "--volume", PIPER_VOLUME,
        "--sentence_silence", "0.2"
    ]

    try:
        # Pass the text to Piper via stdin
        subprocess.run(
            piper_command,
            input=text.encode('utf-8'),
            capture_output=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        print(f"    ❌ Piper Error (ID: {line_id}): Command failed with error code {e.returncode}")
        print(f"       STDOUT: {e.stdout.decode()}")
        print(f"       STDERR: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print(f"    ❌ Piper Error: Executable '{PIPER_EXE}' not found.")
        print("       Please ensure 'piper.exe' is in the script's directory.")
        return False

    if not ENABLE_POST_PROCESSING:
        try:
            os.rename(TEMP_WAV_FILE, final_output_path)
            return True
        except Exception as e:
            print(f"    ❌ File Error: Could not rename temporary file to {final_output_path}. {e}")
            return False

    # --- 2. FFmpeg Post-Processing Command (outputs to final path) ---
    ffmpeg_exe = "ffmpeg" # Relies on the newly fixed system PATH

    # Dynamically prepend atempo filter if speed is adjusted
    speed_filter = ""
    if FFMPEG_SPEED_MULTIPLIER != "1.0":
        speed_filter = f"atempo={FFMPEG_SPEED_MULTIPLIER},"

    # Combine speed filter with existing filters
    full_filter_chain = speed_filter + FFMPEG_AUDIO_FILTERS

    ffmpeg_command = [
        ffmpeg_exe,
        "-y",  # Overwrite output file without asking
        "-i", TEMP_WAV_FILE,
        "-filter:a", full_filter_chain,
        final_output_path
    ]

    try:
        subprocess.run(
            ffmpeg_command,
            capture_output=True,
            check=True
        )
        # Clean up the temporary file after successful processing
        os.remove(TEMP_WAV_FILE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ FFmpeg Error (ID: {line_id}): Command failed with error code {e.returncode}")
        print(f"       STDOUT: {e.stdout.decode()}")
        print(f"       STDERR: {e.stderr.decode()}")
        # Attempt to clean up temp file even if FFmpeg failed
        if os.path.exists(TEMP_WAV_FILE):
            os.remove(TEMP_WAV_FILE)
        return False
    except FileNotFoundError:
        print(f"    ❌ FFmpeg Error: Executable '{ffmpeg_exe}' not found.")
        print("       The system path is incorrect. Check your Path settings.")
        if os.path.exists(TEMP_WAV_FILE):
            os.remove(TEMP_WAV_FILE)
        return False


def main():
    """
    Main function to read the input file and process each line.
    """
    print("=" * 43)
    print("Starting Piper Batch Script...")
    print("=" * 43)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
        print(f"Created output directory: {OUTPUT_PATH}")

    # --- Check for required files/executables ---
    if not os.path.exists(PIPER_EXE):
        print(f"❌ Error: Piper executable not found at {PIPER_EXE}")
        sys.exit(1)

    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model file not found.")
        print(f"       Looking for: {MODEL_PATH}")
        sys.exit(1)

    if not os.path.exists(VOICE_MODEL_CONFIG):
        print(f"❌ Error: Config file not found.")
        print(f"       Looking for: {VOICE_MODEL_CONFIG}")
        sys.exit(1)

    if not os.path.exists(INPUT_FILE_PATH):
        print(f"❌ Error: Input file '{INPUT_FILE_PATH}' not found. Please ensure the CSV file is present.")
        sys.exit(1)
    # --- End Checks ---

    print(f"✅ Found Model: {os.path.basename(MODEL_PATH)}")

    try:
        line_count = 0
        success_count = 0

        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"Found {len(lines)} lines to process in {INPUT_FILE}...")

        for line in lines:
            line_count += 1

            # Using rstrip() to handle potential Windows/Unix line endings
            parts = line.rstrip('\r\n').split(DELIMITER, 1)

            if len(parts) < 2:
                if line.strip():
                    print(f"[{line_count}] Skipping line: Invalid format (missing delimiter or text).")
                continue

            line_id = parts[0].strip()
            text = parts[1].strip()

            if not line_id or not text:
                continue

            print(f"\n[{line_count}] Synthesizing ID: {line_id}...")

            if run_synthesis(line_id, text):
                print(f"    ✅ Saved: {line_id}.wav")
                success_count += 1

        print("\n===========================================")
        print(f"📢 Batch synthesis complete.")
        print(f"Total Lines Attempted: {line_count}")
        print(f"Successfully Saved: {success_count}")
        print("===========================================")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
