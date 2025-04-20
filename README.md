# AcBud: Applied Prompt Compression
By Isabela Yepes and Eric Tang

For the Anthropic Hackathon 2025

AcBud: Accountability Buddy

how to run code:
- git clone (link)
- python3.11 -m venv hack-env
- source hack-env/bin/activate
- pip install -r requirements.txt
- create a .env file and add: 
    ANTHROPIC_API_KEY=your-api-key-here
- create a .gitignore file and add:
    .env
    hack-env
    .DS_Store

Find your API key following instructions here: 
    https://github.com/anthropics/courses/blob/master/anthropic_api_fundamentals/01_getting_started.ipynb


To run demo:
    python acbud_demo.py

To run working api call prototype
    python acbud_api_proto.py