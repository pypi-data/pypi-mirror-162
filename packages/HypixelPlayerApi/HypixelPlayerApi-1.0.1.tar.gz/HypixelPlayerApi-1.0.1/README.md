# Hypixel Player Api (vkeshav300):
> v1.0.1

This is a package made for getting the data of Hypixel Minecraft players in JSON format. You can also get the data of the player's Skyblock profiles.

### To Import:
Step 1) Installation:
```
pip install HypixelPlayerApi
```
Step 2) Importing:
```
from HypixelPlayerApi import main
```

### Code Examples:
```
obj = main.Get_Data(<Player_UUID_Dashed>, <API_KEY>)
PlayerData = obj.get_player_data() # Returns Hypixel player data
SkyblockData = obj.get_skyblock_data(<Profile>) # Returns Hypixel Skyblock data for the inputted profile
```

### Links:
[Issues](https://github.com/vkeshav300/PlayerApiContact/Issues), [Author Profile](https://github.com/vkeshav300)
