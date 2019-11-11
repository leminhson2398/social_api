## Welcome to social_api project

to install and deploy it, please follow the following steps:

1: git clone https://github.com/leminhson2398/social_api.git <br />
2: cd social_api <br />
3: Create virtual environment: **(windows: python -m virtualenv venv)**<br />
4: pip install -r requirements.txt <br />
5: add .env file <br />
6: add serviceAccount.json file **(generated from firebase console)** <br />
7: run **uvicorn social_api.main:app --reload**
