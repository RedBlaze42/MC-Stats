import discord,json,mcplayer

bot=discord.Client()

def load_config():
    with open("config.json","r") as f:
        bot.config=json.load(f)

def save_config():
    with open("config.json","w") as f:
        json.dump(bot.config,f)

load_config()

@bot.event
async def on_ready():
    print("Bot ready")

async def get_player_from_args(args,message):
    if len(args) == 0 or args is None:
        if str(message.author.id) in bot.config["accounts"].keys():
                uuid=bot.config["accounts"][str(message.author.id)]
        else:
            await message.channel.send("Veuillez utiliser la commande `!mcstats assign PSEUDO_MC` pour lier votre compte discord à votre compte minecraft")
            return None
    else:
        uuid=mcplayer.get_uuid_from_name(args[0])
        if uuid is None:
            await message.channel.send("Ce joueur n'existe pas")
            return None
    try:
            player=mcplayer.Player(mcplayer.get_filename_from_uuid(bot.config["stat_path"],uuid))
    except FileNotFoundError:
            await message.channel.send("Ce joueur n'a pas rejoint le serveur")
            return None
    return player

@bot.event
async def on_message(message):
    if message.channel.id==801411399103807501 and message.content.startswith("!mcstats") or message.author.id==153201272399462400:
        args=message.content.split(" ")[1:]
        try:
            if len(args)>0 and args[0]=="assign":
                uuid=mcplayer.get_uuid_from_name(args[1],message)
                if uuid is not None:
                    bot.config["accounts"][str(message.author.id)] = uuid
                    save_config()
                    await message.channel.send("Votre discord __{}__ est associé au compte Minecraft __{}__".format(message.author.name,args[1]))
                else:
                    await message.channel.send("Ce compte n'existe pas")
                    return
            elif len(args)>=2 and args[0]=="top":
                player=await get_player_from_args(args[2:],message)
                if player is None: return

                stat_name="minecraft:{}".format(args[1])
                if stat_name not in player.stat_types:
                    stat_types="\n".join([stat_type.split(":")[1] for stat_type in player.stat_types if stat_type!="minecraft:custom"])
                    await message.channel.send("Ceci n'est pas un type de stats, veuillez choisir parmis:\n```{}```".format(stat_types))
                    return

                embed=discord.Embed(color=4062976,title="Stats \"{}\" de {}".format(stat_name.split(":")[1],player.name))
                embed.set_thumbnail(url="https://minotar.net/helm/{}".format(player.name))
                embed.description=player.format_top_stats(stat_name)

                await message.channel.send(embed=embed)
                
            else:
                player=await get_player_from_args(args[0:],message)
                if player is None: return

                embed=discord.Embed(color=4062976,title="Stats de {}".format(player.name))
                embed.set_thumbnail(url="https://minotar.net/helm/{}".format(player.name))
                embed.description=player.get_custom_stats()

                await message.channel.send(embed=embed)

        except (ValueError, IndexError) as e:
            await message.channel.send("Mauvaise utilisation: "+e.__repr__())

bot.run(bot.config["token"])