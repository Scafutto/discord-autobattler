# Auto Battler for Discord

This project is a simple auto battler for Discord that I used to practice my Python skills. It is a work in progress, and I only had my winter break (about 2 weeks) to work on it, so be aware that the code is not fully commented or even optimized, and definitely not documented.

## Requirements

- A SQL database (`sudo apt install mysql-server`)
- Setup your bot, permissions, and token on Discord. If you don't know how to do it, just follow Discord's guide [here](https://discord.com/developers/docs/getting-started).
- Python (should be installed by default on Ubuntu)
- Install dependencies with `pip install -r requirements.txt`
- Update your database info on `main.py` and `schedule/energy_update`
- Add `schedule/energy_update` to your crontab with `crontab -e`. To run it every 30 minutes: `*/30 * * * * python3 /path/to/bot/dir/schedule/energy_update.py`.

Feel free to use it, make suggestions, or even change it.
