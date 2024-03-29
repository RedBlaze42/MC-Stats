import discord,json,mcplayer,os,glob

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
    await bot.change_presence(activity=discord.Game(name="MINECRAFT"))

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
    if (message.channel.id==801411399103807501 or message.author.id==153201272399462400 or isinstance(message.channel,discord.channel.DMChannel)) and message.content.startswith("!mcstats"):
        args=message.content.split(" ")[1:]
        try:
            if len(args)>0 and args[0]=="assign":
                uuid=mcplayer.get_uuid_from_name(args[1])
                if uuid is not None:
                    bot.config["accounts"][str(message.author.id)] = uuid
                    save_config()
                    await message.channel.send("Votre discord __{}__ est associé au compte Minecraft __{}__".format(message.author.name,args[1]))
                else:
                    await message.channel.send("Ce compte n'existe pas")
                    return
            elif len(args)>=2 and args[0].startswith("top"):
                try:
                    top=int(args[0].split("top")[1])
                except ValueError:
                    top=7
                player=await get_player_from_args(args[2:],message)
                if player is None: return

                stat_name="minecraft:{}".format(args[1])
                if stat_name not in player.stat_types:
                    stat_types="\n".join([stat_type.split(":")[1] for stat_type in player.stat_types if stat_type!="minecraft:custom"])
                    await message.channel.send("Catégories de statistiques:\n```\n{} ```".format(stat_types))
                    return

                embed=discord.Embed(color=4062976,title="Stats \"{}\" de {}".format(stat_name.split(":")[1],player.name))
                embed.set_thumbnail(url="https://minotar.net/helm/{}".format(player.name))
                embed.description=player.format_top_stats(stat_name,top=top)

                await message.channel.send(embed=embed)
            elif len(args)>0 and args[0]=="playerlist":
                player_list=glob.glob(os.path.join(bot.config["stat_path"],"*.json"))
                embed=discord.Embed(color=4062976,title="Liste des joueurs")
                players=[mcplayer.Player(player_path) for player_path in player_list]
                for player in sorted(players,key=lambda player: player.data["minecraft:custom"]["minecraft:play_time"],reverse=True):
                    embed.add_field(inline=False,name=player.name,value="Temps de jeu: {} h".format(round(player.data["minecraft:custom"]["minecraft:play_time"]/72000,1)))
                await message.channel.send(embed=embed)
            elif len(args)>0 and args[0]=="help":
                await message.channel.send("`!mcstats assign PSEUDO_MC` lie votre compte discord avec votre compte minecraft\n`!mcstats PSEUDO_MC` donne un résumé des stats (PSEUDO_MC est facultatif)\n`!mcstats playerlist` donne la liste des joeuurs\n`!mcstats topX TYPE_STATS PSEUDO_MC` donne les X meilleurs stats dans chaque catégorie (pour connaïtre les catégories, tapez `!mcstats top help`)")
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
