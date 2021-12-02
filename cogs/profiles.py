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

import math

load_dotenv()
key = str(os.getenv('RIOT_API'))
watcher = LolWatcher(key)


class Profiles(commands.Cog):
    """Gathers information from a summoner's profile"""
    def __init__(self, client):
        self.client = client   

    @commands.command(name="prettyprofile", aliases=["p","profile","pretty"])
    async def profile(self, ctx, *args):
        """Shows summoner profile in a pretty way"""
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
        summonerLevel = summonerWatch['summonerLevel']
        Icon = summonerWatch['profileIconId']
        # print(summonerWatch)
        stats = watcher.league.by_summoner(Region, SummonerID)
        # print(stats)
        # Get the Solo Queue Values (find the Solo Queue Dictionary within stats)
        res = None
        SOLODUO = True
        for sub in stats:
            if sub['queueType'] == "RANKED_SOLO_5x5":
                res = sub
                break
        if res == None:
            SOLODUO = False
        else: 
            n = stats.index(res)
            soloduotier = stats[n]['tier']
            soloduorank = stats[n]['rank']
            soloduowins = int (stats[n]['wins'])
            soloduolosses = int (stats[n]['losses'])
            soloduolp = stats[n]['leaguePoints']
            soloduowinrate = int (soloduowins/(soloduowins + soloduolosses) *100)

        res = None
        RANKEDFLEX = True
        for sub in stats:
            if sub['queueType'] == "RANKED_FLEX_SR":
                res = sub
                break
        if res == None:
            RANKEDFLEX = False
        else:
            n = stats.index(res)
            rankedflextier = stats[n]['tier']
            rankedflexrank = stats[n]['rank']
            rankedflexwins = int (stats[n]['wins'])
            rankedflexlosses = int (stats[n]['losses'])
            rankedflexlp = stats[n]['leaguePoints']
            rankedflexwinrate = int (rankedflexwins/(rankedflexwins + rankedflexlosses) *100)
        
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        masteriesGrabbing = 3
        mastery = watcher.champion_mastery.by_summoner(Region, SummonerID)
        # print("MASTERY")
        # print(mastery)
        champPoints = []
        champId = []
        # Conviently already sorted in highest to lowest mastery order
        try:
            for x in range(masteriesGrabbing):
                nameofSummoner = mastery[x]['championPoints']
                champPoints.append(nameofSummoner)
                champidentification = mastery[x]['championId']
                champId.append(champidentification)
        except:
            pass
            

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

        for x in range(len(champId)):
            for sub in Champions['data']:
                if int(Champions['data'][sub]['key']) == champId[x]:
                    res = sub
                    break 
            data = Champions['data'][res]['name']
            champNames.append(data)
            print(data)
            
        champEmojiId = []
        
        with open('data/championicons.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(champId)):
            for e in emojis:
                if int(e['KEY']) == champId[i]:
                    emoji_value = e['EMOJICODE']
                    champEmojiId.append(emoji_value)
        f.close()

        inLiveGame = True
        try:
            liveGame = watcher.spectator.by_summoner(Region, SummonerID)
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

            ChampionData = urllib.request.urlopen(f'http://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/champion.json').read()
            Champions = json.loads(ChampionData)
            # print(Champions)

            livechampNames = []
            res = None

            for x in range(len(champids)):
                for sub in Champions['data']:
                    if int(Champions['data'][sub]['key']) == champids[x]:
                        res = sub
                        break 
                data = Champions['data'][res]['name']
                livechampNames.append(data)
                # print(data)

            Currenttime = 0
            timeinseconds = liveGame['gameLength']
            m, s = divmod(timeinseconds, 60)
            y = ""
            if s < 10:
                y = 0
        except:
            inLiveGame = False
            # print("Not in Live Game")

        
        
        temp_embed = discord.Embed(description=f"Fetching your profile, wait a moment...", color=16742893)
        temp_embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        msg = await ctx.send(embed=temp_embed)

        embed = discord.Embed(title=f'Profile: {summonerName}', description=f"Summary of the profile you asked for: \n \u200B", color=16742893)
        embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        embed.add_field(name='Summoner Level', value=f'{summonerLevel}')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='\u200B', value='\u200B')
        if SOLODUO == True:
            embed.add_field(name='Ranked (Solo/Duo)', value = f'{str(soloduotier)} {str(soloduorank)} with {str(soloduolp)} LP and a {str(soloduowinrate)}% winrate')
        else:
            embed.add_field(name='Ranked (Solo/Duo)', value = 'N/A')
        embed.add_field(name='\u200B', value='\u200B')
        if RANKEDFLEX == True:
            embed.add_field(name='Ranked (Flex)', value = f'{str(rankedflextier)} {str(rankedflexrank)} with {str(rankedflexlp)} LP and a {str(rankedflexwinrate)}% winrate')
        else:
            embed.add_field(name='Ranked (Flex)', value = 'N/A')
        try:
            embed.add_field(name='Highest Champion Masteries', value=f'''
                        **[1]**  {champEmojiId[0]} {champNames[0]}: {champPoints[0]} pts
                        **[2]**  {champEmojiId[1]} {champNames[1]}: {champPoints[1]} pts
                        **[3]**  {champEmojiId[2]} {champNames[2]}: {champPoints[2]} pts
                        \u200B''')
        except:
            embed.add_field(name='Highest Champion Masteries', value=f'''NOT ENOUGH CHAMPIONS''')
        embed.add_field(name='\u200B', value='\u200B')
        if inLiveGame == True:
            embed.add_field(name='Live Game', value=f'''
            Playing {champidEmojiIds[0]} {livechampNames[0]} for {m}:{y}{s}
            Summoner Spells: {summspellEmojiIds[0]} and {summspellEmojiIds[1]}
            Main tree:{runestyleEmojiIds[0]} - {runeEmojiIds[0]} {runeEmojiIds[1]} {runeEmojiIds[2]} {runeEmojiIds[3]}
            Secondary tree: {runestyleEmojiIds[1]} - {runeEmojiIds[4]} {runeEmojiIds[5]}
            \u200B''')
        else:
            embed.add_field(name='Live Game', value=f'N/A')
        await asyncio.sleep(1)
        await msg.edit(embed=embed) 

    @commands.command(name="masterychecker", aliases=["mp","mastery","masteries","mcheck","mps"])
    async def mp(self, ctx, *args):
        """This command takes y- mp #ofchamps(or max) summonername"""
        # STATS
        data = list(args)
        arggrabbing = 0
        if (any(map(str.isdigit, args[0])) == True):
            arggrabbing = 1
            intarg = args[0]
            del data[0]
        else:
            intarg = 80
        Region = "na1"
        servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
        summonerrequest = ""
        possibleRegion = args[0]

        print(data)
        if possibleRegion in servers:
            Region = servers[possibleRegion]
            del data[0]
            summonerrequest = listToStr = ' '.join(map(str, data)) 
        else:
            summonerrequest = listToStr = ' '.join(map(str, data))
        print(summonerrequest)
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        # print(intarg)
        masteriesGrabbing = int(intarg)
        summoner = watcher.summoner.by_name(Region, summonerrequest)
        Icon = summoner['profileIconId']
        # print(summoner)
        summonerName = summoner['name']
        SummonerID = summoner['id']
        stats = watcher.league.by_summoner(Region, SummonerID)
        # print(stats)
        mastery = watcher.champion_mastery.by_summoner(Region, SummonerID)
        # print("MASTERY")
        # print(mastery)
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
        # print(Patches)
        CurrentPatch = Patches[0]
        # print(CurrentPatch)
        
        ChampionData = urllib.request.urlopen(f'http://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/champion.json').read()
        Champions = json.loads(ChampionData)
        # print(Champions)

        champNames = []
        res = None



        for x in range(len(champId)):
            for sub in Champions['data']:
                if int(Champions['data'][sub]['key']) == champId[x]:
                    res = sub
                    break 
            data = Champions['data'][res]['name']
            champNames.append(data)
            # print(data)
            
        champEmojiId = []
        
        with open('data/championicons.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for i in range(len(champId)):
            for e in emojis:
                if int(e['KEY']) == champId[i]:
                    emoji_value = e['EMOJICODE']
                    champEmojiId.append(emoji_value)
        f.close()

        """ print("NAMES")
        for sub in Champions['data']:
            text = Champions['data'][sub]['id']
            print(f'{text},', end ="")
            text = Champions['data'][sub]['id']
            print(f'\:{text}:,', end="")
            text = Champions['data'][sub]['key']
            print(f'{text}') """

        temp_embed = discord.Embed(description=f"Fetching your masteries, wait a moment...", color=16742893)
        temp_embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        msg = await ctx.send(embed=temp_embed)

        embed = discord.Embed(title=f'Profile: {summonerName}', description=f"Masteries of the profile you asked for: \n \u200B", color=16742893)
        embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        masteryembeds = []
        for i in range(math.ceil(len(champPoints)/10)):
            masteryembeds.clear()
            for j in range(10):
                try:
                    masteryembeds.append(f'**[{i*10+j+1}]** {champEmojiId[i*10+j]} {champNames[i*10+j]}: {champPoints[i*10+j]} mastery points')
                except:
                    pass
            nl = '\n'
            text = f"{nl}{nl.join(masteryembeds)}"
            embed.add_field(name=f'Top {(i + 1) * 10}', value = f'{text}', inline=False)
        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)

        await asyncio.sleep(1)
        await msg.edit(embed=embed) 

    @commands.command(name="match_history", aliases=["mh","h","history","matchdata"])
    async def match_history(self, ctx, *, args):
        """Grabs the 3 most recent games for a specific profile"""
        # STATS
        Region = "na1"
        accregion = 'na'
        servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
        summonerrequest = ""
        possibleRegion = args[0]
        data = list(args)
        if possibleRegion in servers:
            Region = servers[possibleRegion]
            accregion = possibleRegion
            del data[0]
            summonerrequest = listToStr = ' '.join(map(str, data)) 
        else:
            summonerrequest = listToStr = ' '.join(map(str, data))
        serverregion = {'euw':'EUROPE','br':'AMERICAS', 'na':'AMERICAS', 'eune':'EUROPE', 'jp':'ASIA', 'las':'AMERICAS', 'lan':'AMERICAS', 'oce':'EUROPE', 'tr':'EUROPE', 'kr':'ASIA', 'ru':'EUROPE'}
        RoutingRegion = serverregion[accregion]
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        matchesGrabbing = 3
        summoner = watcher.summoner.by_name(Region, summonerrequest)
        print(summoner)
        summonerName = summoner['name']
        SummonerID = summoner['id']
        LeagueId = summoner['puuid']
        Icon = summoner['profileIconId']
        stats = watcher.league.by_summoner(Region, SummonerID)
        print(stats)
        mastery = watcher.champion_mastery.by_summoner(Region, SummonerID)
        champPoints = []
        champId = []
        # Think it grabs 20 matches
        matches = watcher.match.matchlist_by_puuid(RoutingRegion, LeagueId)
        matchdata = []
        print(matches)
        # Conviently already sorted in highest to lowest mastery order
        for x in range(matchesGrabbing):
            newmatchdata = watcher.match.by_id(RoutingRegion, matches[x])
            matchdata.append(newmatchdata)
            

        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        CurrentPatch = Patches[0]

        matchinfo = []
        newmatchdict = {}
        newsummdict = {}
        print("MATCH DATA")
        for x in range(len(matchdata)):
            newmatchdict.clear()
            newmatchdict = {'summoners':[],'games':[]}
            for i in range(10):
                newsummdict.clear()
                newsummdict['summonername'] = matchdata[x]['info']['participants'][i]['summonerName']
                newsummdict['championid'] = matchdata[x]['info']['participants'][i]['championId']
                newsummdict['championname'] = matchdata[x]['info']['participants'][i]['championName']
                newsummdict['emojiid'] = None
                newmatchdict['summoners'].append(newsummdict.copy())
            for j in range(2):
                text = 'Victory'
                if matchdata[x]['info']['teams'][j]['win'] == False:
                    text = 'Defeat'
                newmatchdict['games'].append(text)
            matchinfo.append(newmatchdict.copy())
        print(matchinfo)

        with open('data/championicons.json', encoding='utf-8') as f:
            emojis = json.load(f)
        for x in range(len(matchinfo)):
            for y in range(10):
                for e in emojis:
                    if int(e['KEY']) == matchinfo[x]['summoners'][y]['championid']:
                        emoji_value = e['EMOJICODE']
                        matchinfo[x]['summoners'][y]['emojiid'] = emoji_value
            
        f.close()

        temp_embed = discord.Embed(description=f"Fetching your match histories, wait a moment...", color=16742893)
        temp_embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        msg = await ctx.send(embed=temp_embed)

        embed = discord.Embed(title=f'Profile: {summonerName}', description=f"Match history of the profile you asked for: \n \u200B", color=16742893)
        embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
        masteryembeds = []
        for j in range(len(matchinfo)):
            games = "none"
            games = matchinfo[j]['games'][0]
            embed.add_field(name=f'Game: {j + 1}', value = f"**Blue Side:** {games}", inline=True)
            embed.add_field(name=f'\u200B', value = f"\u200B", inline=True)
            games = matchinfo[j]['games'][1]
            embed.add_field(name=f'\u200B', value = f"**Red Side:** {games}", inline=True)
            masteryembeds.clear()
            for i in range(5):
                sname = matchinfo[j]['summoners'][i]['summonername']
                emoji = matchinfo[j]['summoners'][i]['emojiid']
                masteryembeds.append(f'**[{i+1}]** {sname} as {emoji}')
            nl = '\n'
            text = f"{nl}{nl.join(masteryembeds)}"
            embed.add_field(name=f'Champions: ', value = f'{text}', inline=True)
            embed.add_field(name=f'\u200B', value = f"\u200B", inline=True)
            masteryembeds.clear()
            for i in range(5):
                sname = matchinfo[j]['summoners'][i+5]['summonername']
                emoji = matchinfo[j]['summoners'][i+5]['emojiid']
                masteryembeds.append(f'**[{i+1}]** {sname} as {emoji}')
            nl = '\n'
            text = f"{nl}{nl.join(masteryembeds)}"
            embed.add_field(name=f'Champions: ', value = f'{text}{nl}{nl}\u200B', inline=True)
        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
        
        await asyncio.sleep(1)
        await msg.edit(embed=embed)

def setup(client):
    client.add_cog(Profiles(client))