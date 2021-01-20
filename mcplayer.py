import requests,json
from os.path import join

def pretty_print(number):
    float_part="."+str(number).split(".")[1] if isinstance(number,float) else ""
    number = str(int(number))[::-1]
    pretty_number = str()
    for group in range(0,len(number),3):
        pretty_number+=number[group:min(group+3,len(number))]+ " "

    return pretty_number.strip()[::-1]+float_part

def get_filename_from_uuid(path,uuid):
    return join(path,uuid[:8]+"-"+uuid[8:8+4]+"-"+uuid[8+4:8+4+4]+"-"+uuid[8+4+4:8+4+4+4]+"-"+uuid[8+4+4+4:]+".json")

def get_name_from_uuid(uuid):
    req=requests.get("https://sessionserver.mojang.com/session/minecraft/profile/{}".format(uuid))
    if req.status_code!=200: return None
    return req.json()["name"]

def get_uuid_from_name(name):
    req=requests.get("https://api.mojang.com/users/profiles/minecraft/{}".format(name))
    if req.status_code!=200: return None
    return req.json()["id"]

class Player():

    def __init__(self,file):
        self.uuid=".".join(file.split("\\")[-1].split(".")[:-1])
        self.name=get_name_from_uuid(self.uuid)
        with open(file,"r") as f:
            self.data=json.load(f)["stats"]
    
        self.stat_types=list(self.data.keys())

    def top_stats(self, stat_type,top=5):
        if stat_type=="minecraft:custom": return list()

        stats=[k for k, v in sorted(self.data[stat_type].items(), key=lambda item: item[1],reverse=True)]

        return stats[:top]

    def format_top_stats(self, stat_type, top=5):
        top=self.top_stats(stat_type,top=top)
        output=list()
        for stat in top:
            output.append("__{}:__ {}".format(stat.split(":")[1],pretty_print(self.data[stat_type][stat])))

        return "\n".join(output)

    def get_custom_stats(self):
        with open("custom_stats.json","r") as f:
            custom_stats = json.load(f)

        output=list()
        for custom_stat in custom_stats:
            if "divide_by" in custom_stat.keys():
                value=round(self.data["minecraft:custom"][custom_stat["id"]]/custom_stat["divide_by"],2)
            elif "multiply_by" in custom_stat.keys():
                value=self.data["minecraft:custom"][custom_stat["id"]]*custom_stat["divide_by"]
            else:
                value=self.data["minecraft:custom"][custom_stat["id"]]

            unit=" "+custom_stat["unit"] if "unit" in custom_stat.keys() else ""
            output.append(custom_stat["name"]+": "+pretty_print(value)+unit)

        return "Distance parcourue: {} blocs\nConteneurs ouverts: {}\nTemps de jeu moyen par sessions: {} min\n{}".format(pretty_print(round(sum([self.data["minecraft:custom"][stat] for stat in self.data["minecraft:custom"] if "one_cm" in stat])/100)),
            pretty_print(sum([self.data["minecraft:custom"][stat] for stat in self.data["minecraft:custom"] if "inspect" in stat or "open" in stat])),
            round(self.data["minecraft:custom"]["minecraft:play_one_minute"]/self.data["minecraft:custom"]["minecraft:leave_game"]/(20*60)),
            "\n".join(output))
