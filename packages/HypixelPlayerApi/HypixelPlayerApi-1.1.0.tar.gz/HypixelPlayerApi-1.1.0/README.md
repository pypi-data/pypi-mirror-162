# Hypixel Player Api (vkeshav300):
> v1.1.0

This is a package made for getting the data of Hypixel Minecraft players in JSON format. You can also get the data of the player's Skyblock profiles.

## General Information:
### To Install:
For Windows / macOS:
```
pip install HypixelPlayerApi
```

### If you get an error:
Make sure you are on the latest version of Python! Also make sure that you have the latest version of this package! To get on the latest version of this package, you can enter the command found below:
```
pip install --upgrade HypixelPlayerApi
```
If you still have an error, go to the Issues link found under the Links section below.

### Changes Since Last Version:
- **ADDED** option to use a player's `username` instead of their `uuid_dashed`.
- **UPDATED** README to be more organized
- **ADDED** `Using The Package` section to tell how to use the package.
- **REMOVED** links that only worked on Github.

### Links:
[Issues](https://github.com/vkeshav300/PlayerApiContact/Issues), [Releases](https://github.com/vkeshav300/PlayerApiContact/releases/), [Author Profile](https://github.com/vkeshav300), [PyPI page](https://pypi.org/project/HypixelPlayerApi/),

## Using The Package:
### To Import:
```
from HypixelPlayerApi import plr
```
### How to instantiate
```
obj = plr.Player([<(Player UUID-Dashed) or (Player Username)>, <(UUID) or (USERNAME)>], <API_KEY>)
```
In argument 1, you input a list, with the player's uuid-dashed or username as the first element in the list, and then you enter a string telling the program that you entered the UUID or Username. You will see examples at the end of the `How to instantiate` section.
To get the `uuid_dashed` of a player, just go to a website like namemc.com and search up the player's username. It should give you their `uuid` & `uuid_dashed`. To get the `API_KEY`, type `/api` in a Hypixel server. If your `API_KEY` gets leaked, create a new one.

```
obj = plr.Player(['TestUser123', 'USERNAME'], <API_KEY>) # With USERNAME
```
```
obj = plr.Player(['abcdefgh-ijkl-mnop-qrst-uvwxyz', 'UUID'], <API_KEY>) # With UUID-Dashed
```

### Code Examples:
```
PlayerData = obj.get_hypixel_stats() # Returns Hypixel player data
```
```
SkyblockData = obj.get_skyblock_data(<Profile>) # Returns Hypixel Skyblock data for the inputted profile
```
