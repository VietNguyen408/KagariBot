# KagariBot

KagariBot is a Discord bot that offers your server a fun quick word game to play in a voice channel!

This is the rule of Kurry game:
- I will give each one of you guys a card that has a word on it.
- Everyone has the the card with the same word except the impostor.
- You have a set amount of time to discuss with your friends to find the impostor.
- After that, you will have to vote for the suspect.
- If the one who get the most vote is the impostor you guys win, otherwise the impostor wins.

Some quick note:
  - The default prefix is *+*.
  - The number of players should be between 3 and 8.
  - use help command for list of commands.

### Invitation link:
  - https://discord.com/api/oauth2/authorize?client_id=785568039714029629&permissions=0&scope=bot


### Commands:
Kagari offers a number of commands for the game:

* *help* - Display the list of commands.
* *start* - Start the game!
* *stop* - Stop the current game.
* *rule* - Display the rule of the game.

### Requirement:

KagariBot requires Python3 to run.

Install the dependencies if you wish to run an instance of the bot yourself.

```sh
$ cd KagariBot
$ pip3 install --updarde pip
$ pip3 install discord, dnspython, pymongo, flask, pynacl, python-dotenv
$ python3 launcher.py
```
