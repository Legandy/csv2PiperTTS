import subprocess
import os
import sys
import glob

# ====================================================================
# --- CONFIGURATION (Adjust these values) ---
# ====================================================================

# AUDIO SETTINGS
# Setting it higher can result in clipping, better use the loudnorm filter instead.
PIPER_VOLUME = "1.0"

# # FFmpeg Settings
ENABLE_POST_PROCESSING = True  # Set to True to enable FFmpeg filters

# FFmpeg SPEED CONTROL
# This adjusts the playback speed of the generated audio.
# 1.0 = Normal Speed.
FFMPEG_SPEED_MULTIPLIER = "1.0"

# FFmpeg Filter Chain
# 1. pan=stereo: Converts Mono input to Stereo output.
# 2. loudnorm: Normalizes to LUFS (integrated loudness) with a true peak ceiling.
# I=-16: Integrated loudness target set to $-16$ LUFS (standard for many podcast and voice broadcasting standards)
# TP=-1.0: True Peak ceiling set to $-1.0$ dBTP to prevent inter-sample clipping
# LRA=11: Loudness Range target, allowing a dynamic range of $11$ LUFS, which keeps speech sounding natural rather than over-compressed
FFMPEG_AUDIO_FILTERS = "pan=stereo|c0=c0|c1=c0,loudnorm=I=-12:TP=-1.0:LRA=11"

# Executables are assumed to be in the system PATH
PIPER_EXE = "piper.exe"
FFMPEG_EXE = "ffmpeg"

# ====================================================================
# --- END CONFIGURATION ---
# ====================================================================

# Construct paths for files relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Dynamically find any .csv file in the directory
csv_files = glob.glob(os.path.join(SCRIPT_DIR, "*.csv"))
if not csv_files:
    print(f"❌ Error: No .csv file found in {SCRIPT_DIR}")
    sys.exit(1)
INPUT_FILE_PATH = csv_files[0]
INPUT_FILE = os.path.basename(INPUT_FILE_PATH)

# Dynamically find any .onnx model file in the directory
onnx_files = glob.glob(os.path.join(SCRIPT_DIR, "*.onnx"))
if not onnx_files:
    print(f"❌ Error: No .onnx model file found in {SCRIPT_DIR}")
    sys.exit(1)
MODEL_PATH = onnx_files[0]
VOICE_MODEL_CONFIG = MODEL_PATH + ".json"

OUTPUT_DIR = "Output"
OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_DIR)
TEMP_WAV_FILE = os.path.join(OUTPUT_PATH, "temp_output.wav")

# Assuming delimiter defaults to ';' but can be adjusted or inferred
DELIMITER = ";"


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
        sys.exit(1)
    except FileNotFoundError:
        print(f"    ❌ Piper Error: Executable '{PIPER_EXE}' not found.")
        print("       Please ensure the directory containing 'piper.exe' is added to your system's PATH environment variable.")
        sys.exit(1)

    if not ENABLE_POST_PROCESSING:
        try:
            os.rename(TEMP_WAV_FILE, final_output_path)
            return True
        except Exception as e:
            print(f"    ❌ File Error: Could not rename temporary file to {final_output_path}. {e}")
            sys.exit(1)

    # --- 2. FFmpeg Post-Processing Command ---
    speed_filter = ""
    if FFMPEG_SPEED_MULTIPLIER != "1.0":
        speed_filter = f"atempo={FFMPEG_SPEED_MULTIPLIER},"

    full_filter_chain = speed_filter + FFMPEG_AUDIO_FILTERS

    ffmpeg_command = [
        FFMPEG_EXE,
        "-y",
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
        if os.path.exists(TEMP_WAV_FILE):
            os.remove(TEMP_WAV_FILE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ FFmpeg Error (ID: {line_id}): Command failed with error code {e.returncode}")
        print(f"       STDOUT: {e.stdout.decode()}")
        print(f"       STDERR: {e.stderr.decode()}")
        if os.path.exists(TEMP_WAV_FILE):
            os.remove(TEMP_WAV_FILE)
        sys.exit(1)
    except FileNotFoundError:
        print(f"    ❌ FFmpeg Error: Executable '{FFMPEG_EXE}' not found.")
        print("         Please ensure the FFmpeg directory is added to your system's PATH environment variable.\nOr add the ffmpeg.exe in the root of this folder.")
        if os.path.exists(TEMP_WAV_FILE):
            os.remove(TEMP_WAV_FILE)
        sys.exit(1)


def main():
    print("=" * 43)
    print("Starting Piper Batch Script...")
    print("=" * 43)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
        print(f"Created output directory: {OUTPUT_PATH}")

    if not os.path.exists(VOICE_MODEL_CONFIG):
        print(f"❌ Error: Config file not found for model: {VOICE_MODEL_CONFIG}")
        sys.exit(1)

    print(f"✅ Found Model: {os.path.basename(MODEL_PATH)}")
    print(f"✅ Found Input File: {INPUT_FILE}")

    try:
        line_count = 0
        success_count = 0

        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"Found {len(lines)} lines to process in {INPUT_FILE}...")

        for line in lines:
            line_count += 1
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