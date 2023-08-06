# Hypixel Player Api (vkeshav300):
> v1.0.6

This is a package made for getting the data of Hypixel Minecraft players in JSON format. You can also get the data of the player's Skyblock profiles.

### To Install:
```
pip install HypixelPlayerApi
```

### To Import:
```
from HypixelPlayerApi import plr
```

### How to instantiate
```
obj = plr.Player(<Player_UUID_Dashed>, <API_KEY>)
```
To get the `uuid_dashed` of a player, just go to a website like namemc.com and search up the player's username. It should give you their `uuid` & `uuid_dashed`. To get the `API_KEY`, type `/api` in a Hypixel server. If your `API_KEY` gets leaked, create a new one.

### Code Examples:
```
PlayerData = obj.get_hypixel_stats() # Returns Hypixel player data
```
```
SkyblockData = obj.get_skyblock_data(<Profile>) # Returns Hypixel Skyblock data for the inputted profile
```

### If you get an error:
Make sure you are on the latest version of Python! Also make sure that you have the latest version of this package! To get on the latest version of this package, you can enter the command found below:
```
pip install --upgrade HypixelPlayerApi
```
If you still have an error, go to the Issues link found under the Links section below.

### Changes Since Last Version:
- **ADDED** `If you get an error` section to README.
- **CHANGED** `To Import` into `To Install`, `To Import`, and `How to instantiate`.
- **Simplified** `get_info()` in `plr.py`

### Links:
[Issues](https://github.com/vkeshav300/PlayerApiContact/Issues), [Releases](https://github.com/vkeshav300/PlayerApiContact/releases/), [Author Profile](https://github.com/vkeshav300), [PyPI page](https://pypi.org/project/HypixelPlayerApi/),

Will work on Github ONLY:
[LICENSE](LICENSE), [pyproject](pyproject.toml), [Source Code](src/HypixelPlayerApi/plr.py)
