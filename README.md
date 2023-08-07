# HNS Hosting Discord Bot

## Setup
Install the python requirements with `pip install -r requirements.txt`
Add your discord token to a .env file in the root directory of the project
```sh
DISCORD_TOKEN=your_token_here
```

Install nginx
```sh
sudo apt update
sudo apt install nginx -y
```

Add permissions to run the bash scripts
```sh
chmod +x *.sh
```

## Run 

You can run the bot with
```sh
python3 main.py
```

To run the bot in the background, you can use `screen`
```sh
screen -S bot
python3 main.py
```
Close the screen with `Ctrl + A + D` (keeps the process running)
Resume the screen with `screen -r bot`