#!/bin/bash
pip install -r requirements.txt
python create_default_avatar.py || echo "Avatar creation skipped"
