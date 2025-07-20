@echo off

cd /d "%spotify_project_dir%"
call venv\Scripts\activate
pythonw extract_with_metadata.py