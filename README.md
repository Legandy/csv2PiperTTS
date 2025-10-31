# **Piper TTS Batch Synthesis**

This repository contains the piper\_batch.py script to automate the generation of game-ready voice lines using **Piper TTS** (Text-to-Speech), applying professional-grade **LUFS loudness normalization** via **FFmpeg**.

## **🛠️ Prerequisites**

Before you begin, ensure you have the following installed and accessible in your system's PATH:

1. **Piper TTS**: The main synthesis executable (piper.exe) and your corresponding **voice model files**.  
   **⚠️ IMPORTANT MODEL NOTE:** The voice model must be in the **.onnx format** (Open Neural Network Exchange), paired with its necessary **.json configuration** file. Other model formats are not compatible with this setup.  
2. **FFmpeg**: A recent, full-featured version of FFmpeg (Version 8.0 or later is recommended).  
3. **Python 3**: To run the batch synthesis script.

## **📁 Project Structure**

This is the recommended file structure. All required files should be placed in the root directory where you execute piper\_batch.py.  
/Your\_Project\_Root  
├── piper\_batch.py          \# The batch script  
├── piper.exe               \# The Piper executable  
├── YourModelName.onnx      \# The Piper voice model (from VOICE\_MODEL\_NAME)  
├── YourModelName.json      \# The Piper model config  
├── voice\_lines.csv         \# The input file (from INPUT\_FILE)  
└── PiperTTS\_output/        \# The output folder (from OUTPUT\_DIR, created upon run)  
    ├── 943635243.wav  
    ├── 102938475.wav  
    └── ...

**⚠️ IMPORTANT:** The VOICE\_MODEL\_NAME you set in the script must correspond to both the **.onnx** model file and the **.json** configuration file being present in the root directory.

## **1\. Batch Synthesis (piper\_batch.py)**

This script handles the heavy lifting of TTS generation and audio quality control.

### **Configuration**

Before running, open piper\_batch.py and adjust the following variables under the CONFIGURATION section:

| Variable | Description | Recommended Value |
| :---- | :---- | :---- |
| **INPUT\_FILE** | The name of your CSV file containing the voice lines. | voice\_lines.csv |
| **OUTPUT\_DIR** | The folder where the final WAV files will be saved. | PiperTTS\_output |
| **VOICE\_MODEL\_NAME** | The base name of your Piper model files (e.g., SubnauticaPDA). | YourModelName |
| **DELIMITER** | The character separating the ID and the Text in your CSV. | ; or , |
| **PIPER\_VOLUME** | Initial volume boost/reduction (1.0 \= original). Use this for minor tweaks. | "2" (For a cleaner start) |
| **ENABLE\_POST\_PROCESSING** | **MUST BE True**. Enables FFmpeg processing (LUFS). | True |
| **FFMPEG\_AUDIO\_FILTERS** | **CRITICAL:** The LUFS normalization filter chain. | See **Audio Quality** section below. |

### **Audio Quality: LUFS Normalization**

The script uses a modern FFmpeg filter for professional loudness leveling:  
FFMPEG\_AUDIO\_FILTERS \= "pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-1.0:LRA=11"

* **I=-16**: Sets the **Integrated Loudness** target to **\-16 LUFS**, which is the widely accepted standard for video game audio.  
* **TP=-1.0**: Sets the **True Peak** limit to $-1.0 \\text{ dBFS}$, guaranteeing the audio never clips digitally.  
* **LRA=11**: Sets the Loudness Range to $11 \\text{ LU}$, ensuring the final audio is consistent.

### **Usage**

1. **Create your input file** (voice\_lines.csv). Format each line as UniqueID;The spoken text.  
   943635243;This is the first voice line.  
   102938475;Systems nominal. Ready for launch.

2. **Run the script** from your terminal in the project root (where piper.exe and piper\_batch.py are located):  
   python piper\_batch.py

3. **Result:** High-quality, LUFS-normalized WAV files will appear in the designated **PiperTTS\_output** directory.