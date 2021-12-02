from datetime import datetime
import discord
from discord.ext import commands
import json
import traceback
import re
import os
from dotenv import load_dotenv
from riotwatcher import LolWatcher
from discord import Embed, Member

import asyncio
import urllib

load_dotenv()
key = str(os.getenv('RIOT_API'))
watcher = LolWatcher(key)


class Old_Commands(commands.Cog):
    def __init__(self, client):
        self.client = client   

    @commands.command()
    async def champ(self, ctx, *, args):
        champ = str(args)
        print(champ)
        Region = 'na1'
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"

        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        # print(Patches)
        CurrentPatch = Patches[0]
        # print(CurrentPatch)

        ChampionData = urllib.request.urlopen(f'http://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/champion.json').read()
        Champions = json.loads(ChampionData)
        # print(Champions["data"]["Ahri"])

        res = None
        for sub in Champions['data']:
            if Champions['data'][sub]['id'].casefold() == champ:
                res = sub
                break
        key = Champions['data'][res]['key']
        print(key)
        await ctx.send(key)

    @commands.command()
    async def basicprofile(self, ctx, *, args):
        """Basic username and level of summoner"""
        # STATS
        summoner = watcher.summoner.by_name('na1', args)
        print(summoner)
        stats = watcher.league.by_summoner('na1', summoner['id'])
        print(stats)
        summonerName = summoner['name']
        SummonerID = summoner['id']
        mastery = watcher.champion_mastery.by_summoner('na1', SummonerID)
        print("MASTERY")
        print(mastery)


        embed = discord.Embed(title='Profile')
        embed.add_field(name = 'Username', value= str(summonerName), inline = True)
        embed.add_field(name = 'Level', value = summoner['summonerLevel'], inline = True)

        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def opgg(self, ctx, *, args):
        """Displays rank and stats of summoner"""
        # STATS
        summoner = watcher.summoner.by_name('na1', args)
        print(summoner)
        stats = watcher.league.by_summoner('na1', summoner['id'])
        print(stats)
        summonerPUUID = summoner['puuid']
        summonerID = summoner['accountId']
        summonerName = summoner['name']
        # Get the Solo Queue Values (find the Solo Queue Dictionary within stats)
        res = None
        for sub in stats:
            if sub['queueType'] == "RANKED_SOLO_5x5":
                res = sub
                break 
        n = stats.index(res)
        tier = stats[n]['tier']
        rank = stats[n]['rank']
        wins = int (stats[n]['wins'])
        losses = int (stats[n]['losses'])
        lp = stats[n]['leaguePoints']
        winrate = int (wins/(wins + losses) *100)

        

        # Discord Message Embed Style 
        embedgg = discord.Embed(
            title = f"{str(summonerName)}", 
            colour = discord.Colour.blue()
        )
        embedgg.add_field(name = 'Solo Queue Rank', value = f'{str(tier)} {str(rank)} with {str(lp)} LP and a {str(winrate)}% winrate', inline = False)

        await ctx.send(embed = embedgg)

    @commands.command()
    async def runes(self, ctx, *, args):
        # STATS
        Region = 'na1'
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        masteriesGrabbing = 10
        summoner = watcher.summoner.by_name(Region, args)
        print(summoner)
        summonerName = summoner['name']
        SummonerID = summoner['id']
        stats = watcher.league.by_summoner(Region, SummonerID)
        print(stats)
        mastery = watcher.champion_mastery.by_summoner(Region, SummonerID)
        print("MASTERY")
        print(mastery)
        champPoints = []
        champId = []
        # Conviently already sorted in highest to lowest mastery order
        for x in range(masteriesGrabbing):
            nameofSummoner = mastery[x]['championPoints']
            champPoints.append(nameofSummoner)
            champidentification = mastery[x]['championId']
            champId.append(champidentification)
            

        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        print(Patches)
        CurrentPatch = Patches[0]
        print(CurrentPatch)
        
        RuneData = urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/runesReforged.json').read()
        Runes = json.loads(RuneData)
        # print(Champions)

        print("Runes")
        for i in range(len(Runes)):
            text = Runes[i]['key']
            print(f'{text},', end ="")
            text = Runes[i]['key']
            print(f'\:{text}:,', end="")
            text = Runes[i]['id']
            print(f'{text}')
            for sub1 in range(len(Runes[i]['slots'])):
                for sub2 in range(len(Runes[i]['slots'][sub1]['runes'])):
                    text = Runes[i]['slots'][sub1]['runes'][sub2]['key']
                    print(f'{text},', end ="")
                    text = Runes[i]['slots'][sub1]['runes'][sub2]['key']
                    print(f'\:{text}:,', end="")
                    text = Runes[i]['slots'][sub1]['runes'][sub2]['id']
                    print(f'{text}')

        runeEmojiId = []
        
        with open('data/runesReforged.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(emojis)):
            for e in emojis:
                emoji_value = e['EMOJICODE']
                runeEmojiId.append(emoji_value)
        f.close()


        embed = discord.Embed(
            title='Profile',
            colour = 16742893
        )
        embed.add_field(name = 'Username', value= str(summonerName), inline = True)
        embed.add_field(name = 'Level', value = summoner['summonerLevel'], inline = True)
        for i in range(20):
            embed.add_field(name = f'{runeEmojiId[i]}', value = '\u200b', inline = False)
        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)


        await ctx.send(embed=embed)

    @commands.command()
    async def sumspells(self, ctx, *, args):
        # STATS
        Region = 'na1'
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        masteriesGrabbing = 10
        summoner = watcher.summoner.by_name(Region, args)
        print(summoner)
        summonerName = summoner['name']
        SummonerID = summoner['id']
        stats = watcher.league.by_summoner(Region, SummonerID)
        print(stats)
        mastery = watcher.champion_mastery.by_summoner(Region, SummonerID)
        print("MASTERY")
        print(mastery)
        champPoints = []
        champId = []
        # Conviently already sorted in highest to lowest mastery order
        for x in range(masteriesGrabbing):
            nameofSummoner = mastery[x]['championPoints']
            champPoints.append(nameofSummoner)
            champidentification = mastery[x]['championId']
            champId.append(champidentification)
            

        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        print(Patches)
        CurrentPatch = Patches[0]
        print(CurrentPatch)
        
        SummData = urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/summoner.json').read()
        SummonerSpells = json.loads(SummData)
        # print(Champions)

        print("SummonerSpells")
        for sub in SummonerSpells['data']:
            text = SummonerSpells['data'][sub]['id']
            print(f'{text},', end ="")
            text = SummonerSpells['data'][sub]['id']
            print(f'\:{text}:,', end="")
            text = SummonerSpells['data'][sub]['key']
            print(f'{text}')

        """ runeEmojiId = []
        
        with open('data/runesReforged.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(emojis)):
            for e in emojis:
                emoji_value = e['EMOJICODE']
                runeEmojiId.append(emoji_value)
        f.close() """


        embed = discord.Embed(
            title='Profile',
            colour = 16742893
        )
        embed.add_field(name = 'Username', value= str(summonerName), inline = True)
        embed.add_field(name = 'Level', value = summoner['summonerLevel'], inline = True)
        """         for i in range(20):
            embed.add_field(name = f'{runeEmojiId[i]}', value = '\u200b', inline = False) """
        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)


        await ctx.send(embed=embed)

    @commands.command()
    async def repeat(self, ctx, message=None):
        message = message or "Hello ;)"
        author = ctx.author
        await ctx.send(f'{author} sent "{message}"')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def elisha(self, ctx):
        await ctx.send('Hi Elisha!')

    @commands.command()
    async def simplify(self, ctx):
        Region = 'na1'
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"

        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        # print(Patches)
        CurrentPatch = Patches[0]
        # print(CurrentPatch)

        Items = urllib.request.urlopen(f'http://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/item.json').read()
        itemData = json.loads(Items)
        itemlist2= [ (id,x['name'])  for id, x in itemData['data'].items() ]
        print(itemlist2)

        itemcount = list(itemData['data'].keys())
        for x in range(len(itemcount)):
            print(itemData['data'][itemcount[x]]['name'])

def setup(client):
    client.add_cog(Old_Commands(client))