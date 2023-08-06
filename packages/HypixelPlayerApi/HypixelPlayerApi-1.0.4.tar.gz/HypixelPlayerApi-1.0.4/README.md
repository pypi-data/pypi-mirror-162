# Hypixel Player Api (vkeshav300):
> v1.0.4

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
obj = plr.Get_Data(<Player_UUID_Dashed>, <API_KEY>)
```
```
PlayerData = obj.get_hypixel_stats() # Returns Hypixel player data
```
```
SkyblockData = obj.get_skyblock_data(<Profile>) # Returns Hypixel Skyblock data for the inputted profile
```

### Changes Since Last Version:
- **CHANGED** "main.py" name to "plr.py"
- **CHANGED** get_player_data method name to get_hypixel_stats
- **KEPT** get_skyblock_data method name as get_skyblock_data
- **UPDATED** README.md & pyproject.toml files
- **SKIPPED** version 1.0.3 because of link that needed updating

### Links:
[Issues](https://github.com/vkeshav300/PlayerApiContact/Issues), [Releases](https://github.com/vkeshav300/PlayerApiContact/releases/), [Author Profile](https://github.com/vkeshav300), [PyPI page](https://pypi.org/project/HypixelPlayerApi/), [LICENSE](LICENSE), [pyproject](pyproject.toml), [Source Code](src/HypixelPlayerApi/plr.py)
