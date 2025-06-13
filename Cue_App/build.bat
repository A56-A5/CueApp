@echo off
REM Build script for Cue App
REM Generates a standalone Windows executable with icon

pyinstaller ^
    --name "CueApp" ^
    --onefile ^
    --noconsole ^
    --icon=logo.ico ^
    cue_app.py

echo Build complete.
pause
