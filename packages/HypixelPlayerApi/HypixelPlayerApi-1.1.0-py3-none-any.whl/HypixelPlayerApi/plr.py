# Importing stuff
import json
from requests import get

class Player():
    def __init__(self, identifier, API_KEY):
        self.identification_method = str(identifier[1])

        if self.identification_method == 'UUID':
            self.uuid_dashed = str(identifier[0])

        elif self.identification_method == 'USERNAME':
            self.username = str(identifier[0])

        else:
            raise TypeError('Argument 1, index 1, is not either "UUID" or "USERNAME".')

        # To get API_KEY type in /api new in Hypixel chat
        self.API_KEY = str(API_KEY)

    def get_info(self, call):
        # Uses requests library and json library to get JSON file from website
        return get(call).json()

    def get_hypixel_stats(self):
        # Gets Player Data
        if self.identification_method == 'UUID':
            hypixel_stats_link = f'https://api.hypixel.net/player?key={self.API_KEY}&uuid={self.uuid_dashed}'

        if self.identification_method == 'USERNAME':
            hypixel_stats_link = f'https://api.hypixel.net/player?key={self.API_KEY}&name={self.username}'

        return self.get_info(hypixel_stats_link)

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
