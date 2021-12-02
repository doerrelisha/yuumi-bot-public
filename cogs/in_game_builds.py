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

import urllib

import asyncio


import DiscordUtils

load_dotenv()
key = str(os.getenv('RIOT_API'))
watcher = LolWatcher(key)


class In_Game_Builds(commands.Cog):
    """Displays in-game info for a specific summoner"""
    def __init__(self, client):
        self.client = client   

    @commands.command(name="all_live", aliases=["al","all","a","alllive"])
    async def all_live(self, ctx, *, args):
        """displays all summoners in the specified summoners game using paginate"""
        Region = "na1"
        servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
        summonerrequest = ""
        possibleRegion = args[0]
        data = list(args)
        if possibleRegion in servers:
            Region = servers[possibleRegion]
            del data[0]
            summonerrequest = listToStr = ' '.join(map(str, data)) 
        else:
            summonerrequest = listToStr = ' '.join(map(str, data))
        summonerWatch = watcher.summoner.by_name(Region, summonerrequest)
        summonerName = summonerWatch['name']
        SummonerID = summonerWatch['id']
        liveGame = watcher.spectator.by_summoner(Region, SummonerID)
        print(liveGame)
        print("LIVE GAME DETAILS")
        Participants = liveGame['participants']
        summnames = []
        runes = []
        runestyles = []
        summspells = []
        champids = []
        Icon =[]

        for i in range(10):
            nameofSummoner = Participants[i]['summonerName']
            summnames.append(nameofSummoner)
            for j in range(len(Participants[i]['perks']['perkIds'])):
                runes.append(Participants[i]['perks']['perkIds'][j])
            runestyles.append(Participants[i]['perks']['perkStyle'])
            runestyles.append(Participants[i]['perks']['perkSubStyle'])
            summspells.append(Participants[i]['spell1Id'])
            summspells.append(Participants[i]['spell2Id'])
            champids.append(Participants[i]['championId'])
            Icon.append(Participants[i]['profileIconId'])

        runeEmojiIds = []
        runestyleEmojiIds = []
        summspellEmojiIds = []
        champidEmojiIds= []
        
        with open('data/runesReforged.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(runes)):
            for e in emojis:
                if int(e['KEY']) == runes[i]:
                    emoji_value = e['EMOJICODE']
                    runeEmojiIds.append(emoji_value)
        for i in range(len(runestyles)):
            for e in emojis:
                if int(e['KEY']) == runestyles[i]:
                    emoji_value = e['EMOJICODE']
                    runestyleEmojiIds.append(emoji_value)
        f.close()

        with open('data/summonerspells.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(summspells)):
            for e in emojis:
                if int(e['KEY']) == summspells[i]:
                    emoji_value = e['EMOJICODE']
                    summspellEmojiIds.append(emoji_value)
        f.close()

        with open('data/championicons.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(champids)):
            for e in emojis:
                if int(e['KEY']) == champids[i]:
                    emoji_value = e['EMOJICODE']
                    champidEmojiIds.append(emoji_value)
        f.close()

        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        # print(Patches)
        CurrentPatch = Patches[0]
        # print(CurrentPatch)

        # Discord Message Embed Style
        embeds = []
        for i in range(5):
            embedNew = discord.Embed(title = f"{str(summonerName)}\'s live game", 
            colour = 16742893).add_field(name = f'Blue Side Player {i+1}\'s Summoner Name:', value = f'{summnames[i]}')
            embedNew.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon[i]}.png')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name = f'Champion:', value = f'{champidEmojiIds[i]}')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name = f'Summoner Spells:', value = f'{summspellEmojiIds[2*i]} and {summspellEmojiIds[2*i+1]}')
            embedNew.add_field(name = f'Main tree: {runestyleEmojiIds[2*i]}', value = f'{runeEmojiIds[9*i]} {runeEmojiIds[9*i + 1]} {runeEmojiIds[9*i + 2]} {runeEmojiIds[9*i + 3]}')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name = f'Secondary tree: {runestyleEmojiIds[2*i+1]}', value = f'{runeEmojiIds[9*i+4]} and {runeEmojiIds[9*i+5]}')
            embeds.append(embedNew)
        for i in range(5):
            embedNew = discord.Embed(title = f"{str(summonerName)}\'s live game", 
            colour = 16742893).add_field(name = f'Red Side Player {i+1}\'s Summoner Name:', value = f'{summnames[i+5]}')
            embedNew.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon[i+5]}.png')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name = f'Champion:', value = f'{champidEmojiIds[i+5]}')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name = f'Summoner Spells:', value = f'{summspellEmojiIds[2*i+10]} and {summspellEmojiIds[2*i+11]}')
            embedNew.add_field(name = f'Main tree: {runestyleEmojiIds[2*i+10]}', value = f'{runeEmojiIds[9*i+45]} {runeEmojiIds[9*i + 46]} {runeEmojiIds[9*i + 47]} {runeEmojiIds[9*i + 48]}')
            embedNew.add_field(name='\u200B', value='\u200B')
            embedNew.add_field(name = f'Secondary tree: {runestyleEmojiIds[2*i+11]}', value = f'{runeEmojiIds[9*i+49]} and {runeEmojiIds[9*i+50]}')
            embeds.append(embedNew)
        
        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        await paginator.run(embeds)
        
    @commands.command(name="individuallive", aliases=["i","il","ilive","indlive","ind_live","individual"])
    async def i_live(self, ctx, *, args):
        """Displays the individual summoner data for the requested summoner"""
        Region = "na1"
        servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
        summonerrequest = ""
        possibleRegion = args[0]
        data = list(args)
        if possibleRegion in servers:
            Region = servers[possibleRegion]
            del data[0]
            summonerrequest = listToStr = ' '.join(map(str, data)) 
        else:
            summonerrequest = listToStr = ' '.join(map(str, data))
        summonerWatch = watcher.summoner.by_name(Region, summonerrequest)
        summonerName = summonerWatch['name']
        SummonerID = summonerWatch['id']
        liveGame = watcher.spectator.by_summoner(Region, SummonerID)
        print(liveGame)
        print("LIVE GAME DETAILS")
        Participants = liveGame['participants']
        summnames = []
        runes = []
        runestyles = []
        summspells = []
        champids = []

        i = 0
        for temp in range(len(Participants)):
            if summonerName == Participants[temp]['summonerName']:
                i = temp
                break
        summnames.append(summonerName)
        for j in range(len(Participants[i]['perks']['perkIds'])):
            runes.append(Participants[i]['perks']['perkIds'][j])
        runestyles.append(Participants[i]['perks']['perkStyle'])
        runestyles.append(Participants[i]['perks']['perkSubStyle'])
        summspells.append(Participants[i]['spell1Id'])
        summspells.append(Participants[i]['spell2Id'])
        champids.append(Participants[i]['championId'])

        runeEmojiIds = []
        runestyleEmojiIds = []
        summspellEmojiIds = []
        champidEmojiIds= []
        
        with open('data/runesReforged.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(runes)):
            for e in emojis:
                if int(e['KEY']) == runes[i]:
                    emoji_value = e['EMOJICODE']
                    runeEmojiIds.append(emoji_value)
        for i in range(len(runestyles)):
            for e in emojis:
                if int(e['KEY']) == runestyles[i]:
                    emoji_value = e['EMOJICODE']
                    runestyleEmojiIds.append(emoji_value)
        f.close()

        with open('data/summonerspells.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(summspells)):
            for e in emojis:
                if int(e['KEY']) == summspells[i]:
                    emoji_value = e['EMOJICODE']
                    summspellEmojiIds.append(emoji_value)
        f.close()

        with open('data/championicons.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(champids)):
            for e in emojis:
                if int(e['KEY']) == champids[i]:
                    emoji_value = e['EMOJICODE']
                    champidEmojiIds.append(emoji_value)
        f.close()

        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        # print(Patches)
        CurrentPatch = Patches[0]
        # print(CurrentPatch)

        ChampionData = urllib.request.urlopen(f'http://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/champion.json').read()
        Champions = json.loads(ChampionData)
        # print(Champions)

        champNames = []
        res = None

        for x in range(len(champids)):
            for sub in Champions['data']:
                if int(Champions['data'][sub]['key']) == champids[x]:
                    res = sub
                    break 
            data = Champions['data'][res]['name']
            champNames.append(data)
            print(data)

        Currenttime = 0
        timeinseconds = liveGame['gameLength']
        m, s = divmod(timeinseconds, 60)
        y = ""
        if s < 10:
            y = 0

        Icon = summonerWatch['profileIconId']
        # Discord Message Embed Style
        temp_embed = discord.Embed(description=f"Fetching your live game info, wait a moment...", color=16742893)
        temp_embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        msg = await ctx.send(embed=temp_embed)


        embeds = []
        embedNew = discord.Embed(title=f'{summonerName}\'s live game:', description=f"In game for {m}:{y}{s}", color=16742893).add_field(name = f'Champion:', value = f'Playing as {champidEmojiIds[0]} {champNames[0]}', inline = False)
        embedNew.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        embedNew.add_field(name = f'Summoner Spells:', value = f'{summspellEmojiIds[0]} and {summspellEmojiIds[1]}', inline = False)
        embedNew.add_field(name = f'Main tree: {runestyleEmojiIds[0]}', value = f'{runeEmojiIds[0]} {runeEmojiIds[1]} {runeEmojiIds[2]} {runeEmojiIds[3]}')
        embedNew.add_field(name='\u200B', value='\u200B')
        embedNew.add_field(name = f'Secondary tree: {runestyleEmojiIds[1]}', value = f'{runeEmojiIds[4]} and {runeEmojiIds[5]}')
        embeds.append(embedNew)
        
        await asyncio.sleep(1)
        await msg.edit(embed=embedNew) 

    @commands.command(name="live", aliases=["li","l","lv"])
    async def live(self, ctx, *, args):
        """Displays all the current summoners in a specific game"""
        Region = "na1"
        servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
        summonerrequest = ""
        possibleRegion = args[0]
        data = list(args)
        if possibleRegion in servers:
            Region = servers[possibleRegion]
            del data[0]
            summonerrequest = listToStr = ' '.join(map(str, data)) 
        else:
            summonerrequest = listToStr = ' '.join(map(str, data))
        summonerWatch = watcher.summoner.by_name(Region, summonerrequest)
        summonerName = summonerWatch['name']
        SummonerID = summonerWatch['id']
        liveGame = watcher.spectator.by_summoner(Region, summonerrequest)
        print("LIVE GAME DETAILS")
        Participants = liveGame['participants']
        totalsummonernames = []
        for x in range(10):
            nameofSummoner = Participants[x]['summonerName']
            totalsummonernames.append(nameofSummoner)

        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"

        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        # print(Patches)
        CurrentPatch = Patches[0]
        # print(CurrentPatch)

        Icon = summonerWatch['profileIconId']

        Currenttime = 0
        timeinseconds = liveGame['gameLength']
        m, s = divmod(timeinseconds, 60)
        y = ""
        if s < 10:
            y = 0

        # Discord Message Embed Style 
        temp_embed = discord.Embed(description=f"Fetching your live game info, wait a moment...", color=16742893)
        temp_embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        msg = await ctx.send(embed=temp_embed)

        embed = discord.Embed(title=f'Profile: {summonerName}', description=f"In game for {m}:{y}{s}", color=16742893)
        embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        masteryembeds = []
        for i in range(2):
            masteryembeds.clear()
            for j in range(5):
                masteryembeds.append(f'**[{j+1}]** {totalsummonernames[i*5+j]}')
            nl = '\n'
            text = f"{nl}{nl.join(masteryembeds)}"
            side = None
            if i == 0:
                side = "Blue Side"
            else:
                side = "Red Side"
            embed.add_field(name=f'{side} Champions:', value = f'{text}', inline=False)
            embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)

        await asyncio.sleep(1)
        await msg.edit(embed=embed)    

def setup(client):
    client.add_cog(In_Game_Builds(client))