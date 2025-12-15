## HOUSE PRICE PREDICTOR

House Price Predictor is a machine learning application that predicts real estate prices in Moscow based on user-specified parameters. 
Users interact with the application through a Telegram bot @housepricepredictor_bot.

## HOW RUN APP

1. You need clone this repository to your machine
2. You should create `.env` file in root of project. This file should contain the TOKEN variable for the bot (See `env-template` file). This token is only available from the project maintainers.
3. You need create virtual env and install project dependencies:
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
4. You may run bot following command:
```
python3 Bot/run.py
```

