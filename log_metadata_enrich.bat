@echo off

cd /d "%spotify_project_dir%"
call venv\Scripts\activate
python extract_with_metadata.py >> metadata_enrich_log.txt 2>&1
