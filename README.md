### < 🚧🚧 archival notice: https://github.com/lucashuy/burntbot/issues/22 🚧🚧 >

# burntbot
Manage swaps, auto-returns and more with `burntbot`, a Python bot that interacts with the Shakepay API.  
Visit [https://burntbot.itslucas.win/](https://burntbot.itslucas.win/) for a demonstration of the bot's web capabilities.

## Features
* Auto-return swaps of any amount to the sender
* Initiate swaps quickly with fewer button presses
* Check balances and see who owes you
* Auto-shake using the bot to get shaking sats

## Installation
Please refer to [INSTALLING.md](INSTALLING.md) for instructions on how to install the bot.

## Quick Start
This is meant for a quick refresher for those that already have the bot installed. It is highly recommended you view the [INSTALLING.md](INSTALLING.md) document before you continue.

Running `python start.py` will start the bot. Startup flags can be found below:
```
python start.py [-v | --verbose] [-l | --listen] [-r=host:port] [-d | --demo]
	-v, --verbose	turns on verbose mode, which prints more information
	-l, --listen	turns on listen mode, which turns off the bot's auto-return feature
	-r=host:port	change the host address and port which the web UI binds to
	-d, --demo	sets the bot into demonstration/showcase mode
```

This project also has a web UI. This can be found on port `5000`. The web UI binds itself to `0.0.0.0` by default, this means that you can connect to it from any device on the same network if you go to the local machine's IP address in a web browser.

## Contributing
Missing a feature you want? Something broken? Create an issue or pull request and help grow this project.

## License
This entire project is licensed under AGPL-3.0-or-later.

## Acknowledgements
This project contains code or assets that are not mine, but reproduced or copied with permission:
* [Font Awesome Free](https://fontawesome.com/license/free)
* [css-spinner](https://github.com/loadingio/css-spinner/)
* [Twemoji](https://github.com/twitter/twemoji)

I would like to thank those in the community that extend their hand to help those that want to install this bot. Special thanks to [@domi167](https://github.com/dlabrie) for the API that this bot draws from for swapper reputation and the bot list.  

Finally, thanks to [Shakepay](https://shakepay.com/) for their swapping event that inadvertently created a dedicated swapping community (oh and I guess they also created the API this bot relies on).
