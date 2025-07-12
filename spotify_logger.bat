@echo off

cd /d "%spotify_project_dir%"
call venv\Scripts\activate
python extract_script.py >> auto_extract_log.txt 2>&1
