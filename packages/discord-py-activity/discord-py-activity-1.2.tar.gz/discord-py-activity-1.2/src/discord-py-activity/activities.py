import requests
from requests.structures import CaseInsensitiveDict
import discord

class get_id_of:
    def __init__(self):
        self.Watch_Together = 880218394199220334
        self.Poker_Night = 755827207812677713
        self.Betrayal_io = 773336526917861400
        self.Fishington_io = 814288819477020702
        self.Chess_In_The_Park = 832012774040141894
        self.Sketchy_Artist = 879864070101172255
        self.Awkword = 879863881349087252
        self.Delete_Me_Calla = 832012854282158180
        self.Doodle_Crew = 878067389634314250
        self.Sketch_Heads = 902271654783242291
        self.Letter_League = 879863686565621790
        self.Word_Snacks = 879863976006127627
        self.SpellCast = 852509694341283871
        self.Checkers_In_The_Park = 832013003968348200
        self.Blazing_8s = 832025144389533716
        self.Putt_Party = 945737671223947305
        self.Land_io = 903769130790969345
        self.Bobble_League = 947957217959759964
        self.Ask_Away = 976052223358406656
        self.Know_What_I_Meme = 950505761862189096

    def to_dict(self) -> dict:
        return {"Watch_Together": 880218394199220334,
         "Poker_Night": 755827207812677713,
         "Betrayal_io": 773336526917861400,
         "Fishington_io": 814288819477020702,
         "Chess_In_The_Park": 832012774040141894,
         "Sketchy_Artist": 879864070101172255,
         "Awkword": 879863881349087252,
         "Delete_Me_Calla": 832012854282158180,
         "Doodle_Crew": 878067389634314250,
         "Sketch_Heads": 902271654783242291,
         "Letter_League": 879863686565621790,
         "Word_Snacks": 879863976006127627,
         "SpellCast": 852509694341283871,
         "Checkers_In_The_Park": 832013003968348200,
         "Blazing_8s": 832025144389533716,
         "Putt_Party": 945737671223947305,
         "Land_io": 903769130790969345,
         "Bobble_League": 947957217959759964,
         "Ask_Away": 976052223358406656,
         "Know_What_I_Meme": 950505761862189096}



class activity_obj:
    def __init__(self, resp: dict, channel: discord.TextChannel):
        self.icon_url = "https://cdn.discordapp.com/app-icons/" + resp["target_application"]["id"] + '/' + resp["target_application"]["icon"]
        self.name = resp["target_application"]["name"]
        self.code = resp["code"]
        self.created_at = resp["created_at"]
        self.expires_at = resp["expires_at"]
        self.link = "https://discord.gg/" + resp["code"]
        self.channel = channel

    def make_embed(self) -> discord.Embed:
        embed_var = discord.Embed(title=self.name, description=f"[לחצו כאן]({self.link})")
        embed_var.add_field(name="created at:", value=self.created_at[:10])
        embed_var.add_field(name="end at:", value=self.expires_at[:10])
        embed_var.add_field(name="Channel:", value=self.channel.mention)
        embed_var.set_thumbnail(url=self.icon_url)
        return embed_var


class activity:
    def __init__(self, token: str):
        self.token = token

    def new_link(self, channel_obj, activity_id) -> activity_obj:
        channel_id = channel_obj.id
        url = f"https://discord.com/api/v9/channels/{channel_id}/invites"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bot {self.token}"
        headers["Content-Type"] = "application/json"
        data = "{" + f"""
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "{activity_id}",
            "target_type": 2,
            "temporary": false,
            "validate": null
            """ + "}"
        resp = requests.post(url, headers=headers, data=data)
        return activity_obj(resp.json(), channel_obj)
