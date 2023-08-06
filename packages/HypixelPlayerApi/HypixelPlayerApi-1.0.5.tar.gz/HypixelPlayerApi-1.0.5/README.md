# Hypixel Player Api (vkeshav300):
> v1.0.5

This is a package made for getting the data of Hypixel Minecraft players in JSON format. You can also get the data of the player's Skyblock profiles.

### To Import:
Step 1) Installation:
```
pip install HypixelPlayerApi
```
Step 2) Importing:
```
from HypixelPlayerApi import plr
```

### Code Examples:
```
obj = plr.Player(<Player_UUID_Dashed>, <API_KEY>)
```
```
PlayerData = obj.get_hypixel_stats() # Returns Hypixel player data
```
```
SkyblockData = obj.get_skyblock_data(<Profile>) # Returns Hypixel Skyblock data for the inputted profile
```

### Changes Since Last Version:
- **FIXED** line 18 in README to be plr.Player not plr.Get_Data

### Links:
[Issues](https://github.com/vkeshav300/PlayerApiContact/Issues), [Releases](https://github.com/vkeshav300/PlayerApiContact/releases/), [Author Profile](https://github.com/vkeshav300), [PyPI page](https://pypi.org/project/HypixelPlayerApi/), [LICENSE](LICENSE), [pyproject](pyproject.toml), [Source Code](src/HypixelPlayerApi/plr.py)
