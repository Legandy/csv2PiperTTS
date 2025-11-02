@echo off
setlocal
echo Starting conversion of all WAV files to WEM...

zSound2wem.cmd *.wav

echo.
echo Conversion process complete.
pause