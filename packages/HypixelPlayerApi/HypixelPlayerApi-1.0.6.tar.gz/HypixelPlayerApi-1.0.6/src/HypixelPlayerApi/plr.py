# Importing stuff
import json
from requests import get

class Player():
    def __init__(self, uuid_dashed, API_KEY):
        # To get uuid_dashed is used to identify the player- Pubically availible on sites like namemc.com
        self.uuid_dashed = str(uuid_dashed)

        # To get API_KEY type in /api new in Hypixel chat
        self.API_KEY = str(API_KEY)

    def get_info(self, call):
        # Uses requests library and json library to get JSON file from website
        return get(call).json()

    def get_hypixel_stats(self):
        # Gets Player Data
        uuid_link = f'https://api.hypixel.net/player?key={self.API_KEY}&uuid={self.uuid_dashed}'
        return self.get_info(uuid_link)

    def get_skyblock_data(self, PreferredProfile):
        # Gets Skyblock Profile Data
        PlayerInfo = self.get_hypixel_stats()

        try:
            ProfileSection = PlayerInfo['player']['stats']['SkyBlock']['profiles']

        except:
            raise TypeError('Player does not have skyblock data')

        PreferredProfileData = None

        # Checks all profiles to see if the player actually has the profile
        for v in ProfileSection.values():
            if v['cute_name'] == str(PreferredProfile):
                PreferredProfileData = v['profile_id']
                break

        if PreferredProfileData == None:
            return f'Could Not Find {PreferredProfile} for {self.uuid_dashed}.'

        skyblock_profile_link = f'https://api.hypixel.net/skyblock/profile?key={self.API_KEY}&profile={PreferredProfileData}'

        return self.get_info(skyblock_profile_link)
