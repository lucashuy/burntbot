# burntbot - Changelog

## 0.9.4 (March 11th 2022)
Changes:
* Fixed issue where the bot would try to parse an empty list of transactions

## 0.9.3 (October 7th 2021)
Changes:
* Fixed issue where card transactions lacked the `timestamp` key, changed all access to `timestamp` to `createdAt` instead

## 0.9.2 (September 11th 2021)
Changes:
* Fixed issue where API can return shaketags that have trailing spaces causing the `/list` page to be unaccessible

## 0.9.1 (September 10th 2021)
Changes:
* Fixed web UI not sending a swap correctly

## 0.9.0 (September 10th 2021)
Additions:
* Added favicon
* Added button to delete entire list
* Added button to ignore warning from the database and send to user anyways
* Added menu to reorder the send list
* Added version checking when the bot first starts up

Changes:
* Changed email confirmation to repeatedly ask user if they hit enter too early
* Added checks to kill extra threads if the bot is dead
* Reduced shaking intervals to eight hours (from 12)
* Made web UI display a "down" page if the bot is down and restarting
* Changed startup to detect if the user has been logged out/the token is invalid
* Changed storage system to use SQLite instead of custom solution
* Fixed bug where the bot would consider a late return as a completed swap
* Changed waitlist API call to accept compressed data, reducing response size by ~5x
* Lowered the amount of shaketags sent to domi's database to reduce bandwidth and load
* Changed heart beat options to report position, points and completed swaps for the day
* Added timeout to hopefully fix "stuck" bots
* Fixed broken login by readding mobile related headers

## 0.8.4 (July 19th 2021)
Changes:
* Fixed instances of double sending by re-adding transaction cache

## 0.8.3 (July 15th 2021)
Changes:
* Fixed instance of double send by checking transaction dates

## 0.8.2 (July 14th 2021)
Changes:
* Fixed poll rate setting not changing (frontend still checked for >= 4)

## 0.8.1 (July 14th 2021)
Changes:
* Update API parameters according to new spec
* Changed minimum poll rate to 1 second
* Change list sending behaviour: when the account runs out of money it will check to see if anyone returned money, continuing if it still has money
* Removed web UI output from logs if not in verbose mode (actually disabled it this time)

## 0.8.0 (July 7th 2021)
Additions:
* Added the ability to swap to people in a list
* Added banner to startup logs

Changes:
* Fixed initial startup pulling transactions from before the swapping start date
* Removed unofficial pizza paddle
* Clarified documentation to note that blacklist only considers transactions during the swapping period
* Changed web UI thread to follow other thread behaviour: only startup after bot ready

## 0.7.4 (July 3rd 2021)
Changes:
* Improved login process which involves waiting for email confirmation
* Fixed "recieved" typo
* Made heart beat and shaking threads only run on bot ready
* Change console log messages related to threads more user friendly
* Changed `source` when fetching from the swapper database from bot version to bot ID

## 0.7.3 (June 29th 2021)
Additions:
* Added option to only report waitlist position

Changes:
* Made the check feature automatic when looking up shaketags
