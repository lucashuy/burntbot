# burntbot - Installing
This install guide is written for Windows. The steps differ for MacOS and Linux distros, but the main idea is still there.

## Table of Contents
1. [Installing Python](##1-installing-python)
2. [Download the bot source code](##2-download-the-bot-source-code)
3. [Installing required packages](##3-installing-required-packages)
4. [Add people and their balances](##4-add-people-and-their-balances)

## 1. Installing Python
You need to install Python 3. It must be at least version 3.6. You can find a link to download the Python installer [here](https://www.python.org/downloads/). When you start the installer, make sure you check the option to include Python in the PATH. This will make the Python and `pip` executables run from anywhere.

> ![](.github/install_guide/install_python.png)  
> The installer window with the PATH option highlighted.

## 2. Download the bot source code
Now download the source code of the bot and extract it somewhere. The zipped source code can be downloaded with [this link](https://github.com/itslupus/burntbot/archive/refs/heads/master.zip) or by clicking the green code button.

I would normally recommend using `git` to clone and fetch new updates, but that'll probably be too complex for some folks.

> ![](.github/install_guide/download_source.png)  
> The `Download ZIP` button highlighted.

## 3. Installing required packages
Next we need to install the packages required to run the bot. Start by opening up a command prompt (or powershell) window in the same folder of the source of the bot. This can be done easily by typing `cmd` in the address bar.

Once a terminal window is open, type `pip install -r requirements.txt` to install the packages from the file.

> TODO: add gif here

## 4. Add people and their balances
Since not everyone is crazy and only swaps CAD with each other to move up the waitlist, some of you might have some money that you sent to a friend or vice versa. You need to tell the bot that, otherwise the bot might return that $10 uncle Tommy sent you for gas money.

To do this, first start up the bot in listen mode. This mode will not return any money to anyone. Do this by typing `python start.py --listen`. Now, you will need to wait until the bot says that it is ready, this will happen when it is finished fetching your transactions.