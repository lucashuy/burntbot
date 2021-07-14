# burntbot - Changelog

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
