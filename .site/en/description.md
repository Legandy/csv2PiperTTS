# **Piper TTS Batch Synthesis Script**

This script automates the process of turning a list of text lines (from a .csv file) into high-quality, normalized .wav audio files using the **Piper Text-to-Speech** engine and **FFmpeg** for professional audio processing.  
It is designed to produce voice lines that match the loudness and style of existing game audio.

## **🚀 Quick Start Guide**

### **1\. Prerequisites (What You Need)**

Before running the script, ensure you have the following tools installed and correctly configured:

| Tool | Purpose | Setup Note |
| :---- | :---- | :---- |
| **Python 3** | To run the main script (.py). | Ensure it's installed on your system. |
| **Piper TTS** | The text-to-speech engine (piper.exe). | **MUST be accessible via your System PATH.** |
| **FFmpeg** | Audio processing (loudness normalization, speed). | **MUST be accessible via your System PATH.** |

🔴 Critical Setup: The System PATH  
Both piper.exe and ffmpeg.exe must be located in a directory that is included in your computer's System PATH environment variable. If you don't know what this is, look up "Add to system PATH" for Windows/macOS/Linux. If you skip this, the script will show a FileNotFoundError.

### **2\. Project File Structure**

Set up your project directory like this. All files listed below must be in the same folder:  
TTS\_PROJECT/  
├── piper\_batch.py         \<-- (1) The script you run  
├── voice\_lines.csv        \<-- (2) Your input text file  
├── SubnauticaPDA.onnx     \<-- (3) Your Piper Voice Model (The big file)  
├── SubnauticaPDA.onnx.json\<-- (4) Your Piper Config File (The required settings file)  
└── PiperTTS\_output/       \<-- (5) Folder where final .wav files will be saved

### **3\. Configuration in piper\_batch.py**

Before running the script, open piper\_batch.py and modify the three main configuration variables at the top:

#### **A. Voice Model Name**

Set this to the base name of your model files (without extensions).  
VOICE\_MODEL\_NAME \= "voice_model"   
\# The script will automatically look for: voice_model.onnx and voice_model.onnx.json

**🚨 Important Naming Note:** The voice model must be in the **.onnx format** (Open Neural Network Exchange), paired with its necessary **.onnx.json configuration** file. Other model formats are not compatible with this setup.

#### **B. Input CSV**

Ensure the script is pointing to the correct file name.  
INPUT\_FILE \= "voice\_lines.csv"   
DELIMITER \= ";"  \# Change this if your CSV uses commas (",") instead of semicolons (";")

#### **C. Loudness Target (LUFS)**

These settings guarantee your generated audio matches the loudness of your game's original audio.  
\# I (Integrated Loudness) is the target volume of your original game audio.  
\# TP (True Peak) is the unclipped maximum ceiling. Set to \-1.0 for safety.  
FFMPEG\_AUDIO\_FILTERS \= "pan=stereo|c0=c0|c1=c0,loudnorm=I=-10.8:TP=-1.0:LRA=11"

**How to Find Your Game's Loudness:** Run an original audio file through FFmpeg's analysis mode (e.g., using the separate lufs\_analyzer.sh tool) to find the exact Input Integrated value (-10.8 is an example).

### **4\. Running the Script**

1. **Prepare your CSV:** Make sure voice\_lines.csv is formatted as: \[AUDIO\_ID\];\[Text to synthesize\].  
   ID\_001;Welcome aboard, Captain.  
   ID\_002;Proceeding with resource scan.

2. **Open your terminal/command prompt** in the project directory.  
3. **Execute the script:**  
   python piper\_batch.py  
