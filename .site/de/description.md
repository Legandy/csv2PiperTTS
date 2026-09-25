# **Piper TTS Batch Synthesis Script**

Dieses Skript automatisiert den Prozess, bei dem eine Liste von Textzeilen (aus einer CSV-Datei) mithilfe der **Piper Text-to-Speech**-Engine und **FFmpeg** für die professionelle Audiobearbeitung in hochwertige, normalisierte WAV-Audiodateien umgewandelt wird.
Es wurde entwickelt, um Sprachzeilen zu erzeugen, die in Lautstärke und Stil zu den vorhandenen Spiel-Audiodaten passen.

## **🚀 Schnellstartanleitung**

### **1\. Voraussetzungen (Was Sie benötigen)**

Bevor Sie das Skript ausführen, stellen Sie sicher, dass die folgenden Tools installiert und korrekt konfiguriert sind:

| Tool | Zweck | Hinweis zur Einrichtung |
| :---- | :---- | :---- |
| **Python 3** | Zum Ausführen des Hauptskripts (.py). | Stellen Sie sicher, dass es auf Ihrem System installiert ist. |
| **Piper TTS** | Die Text-to-Speech-Engine (piper.exe). | **MUSS über Ihren System-PATH erreichbar sein.** |
| **FFmpeg** | Audioverarbeitung (Lautstärkenormalisierung, Geschwindigkeit). | **MUSS über Ihren System-PATH erreichbar sein.** |

🔴 Wichtige Einstellung: Der System-PATH
Sowohl piper.exe als auch ffmpeg.exe müssen sich in einem Verzeichnis befinden, das in der Umgebungsvariable „System-PATH“ Ihres Computers enthalten ist. Wenn Sie nicht wissen, was das ist, suchen Sie unter Windows/macOS/Linux nach „Zum System-PATH hinzufügen“. Wenn Sie diesen Schritt überspringen, gibt das Skript einen FileNotFoundError aus.

### **2\. Projektdateistruktur**

Richten Sie Ihr Projektverzeichnis wie folgt ein. Alle unten aufgeführten Dateien müssen sich im selben Ordner befinden:
TTS\_PROJECT/
├── piper\_batch.py         \<-- (1) Das Skript, das Sie ausführen
├── voice\_lines.csv        \<-- (2) Ihre Eingabetextdatei
├── SubnauticaPDA.onnx     \<-- (3) Ihr Piper-Sprachmodell (Die große Datei)
├── SubnauticaPDA.onnx.json\<-- (4) Ihre Piper-Konfigurationsdatei (Die erforderliche Einstellungsdatei)
└── PiperTTS\_output/       \<-- (5) Ordner, in dem die fertigen .wav-Dateien gespeichert werden

### **3\. Konfiguration in piper\_batch.py**

Bevor du das Skript ausführst, öffne piper\_batch.py und passe die drei wichtigsten Konfigurationsvariablen am Anfang an:

#### **A. Name des Sprachmodells**

Setze diesen Wert auf den Basisnamen deiner Modelldateien (ohne Dateiendungen).
VOICE\_MODEL\_NAME \= „voice_model“
\# Das Skript sucht automatisch nach: voice_model.onnx und voice_model.onnx.json

**🚨 Wichtiger Hinweis zur Benennung:** Das Sprachmodell muss im **.onnx-Format** (Open Neural Network Exchange) vorliegen und mit der dazugehörigen **.onnx.json-Konfigurationsdatei** gepaart sein. Andere Modellformate sind mit dieser Konfiguration nicht kompatibel.

#### **B. Eingabe-CSV**

Stellen Sie sicher, dass das Skript auf den richtigen Dateinamen verweist.
INPUT\_FILE \= „voice\_lines.csv“
DELIMITER \= „;“  \# Ändern Sie dies, wenn Ihre CSV-Datei Kommas („,“) anstelle von Semikolons („;“) verwendet

#### **C. Lautstärkeziel (LUFS)**

Diese Einstellungen stellen sicher, dass Ihr generiertes Audiomaterial der Lautstärke des Original-Audios Ihres Spiels entspricht.
\# I (Integrated Loudness) ist die Ziellautstärke Ihres Original-Spielaudios.
\# TP (True Peak) ist die maximale Obergrenze ohne Übersteuerung. Setze diesen Wert aus Sicherheitsgründen auf \-1,0.
FFMPEG\_AUDIO\_FILTERS \= „pan=stereo|c0=c0|c1=c0,loudnorm=I=-10,8:TP=-1,0:LRA=11“

**So ermitteln Sie die Lautstärke Ihres Spiels:** Führen Sie eine Original-Audiodatei im Analysemodus von FFmpeg aus (z. B. mit dem separaten Tool „lufs\_analyzer.sh“), um den genauen Wert für „Input Integrated“ zu ermitteln (-10,8 ist ein Beispiel).

### **4\. Ausführen des Skripts**

1. **Bereiten Sie Ihre CSV-Datei vor:** Stellen Sie sicher, dass „voice\_lines.csv“ wie folgt formatiert ist: \[AUDIO\_ID\];\[Zu synthetisierender Text\].
   ID\_001;Willkommen an Bord, Captain.
   ID\_002;Ich führe nun einen Ressourcenscan durch.

2. **Öffnen Sie Ihr Terminal/Ihre Eingabeaufforderung** im Projektverzeichnis.
3. **Führen Sie das Skript aus:**
   python piper\_batch.py