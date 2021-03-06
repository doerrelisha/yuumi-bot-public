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

import DiscordUtils

import pymysql
import requests
import math 

from operator import itemgetter

load_dotenv()
key = str(os.getenv('RIOT_API'))
watcher = LolWatcher(key)

host = str(os.getenv('HOST'))
database = str(os.getenv('DATABASE'))
user = str(os.getenv('USER'))
password = str(os.getenv('PASSWORD'))
port = int(os.getenv('PORT'))


class Leaderboard(commands.Cog):
    """Controls server leaderboard"""
    def __init__(self, client):
        self.client = client   

    @commands.command()
    async def add(self, ctx, region=None, *, summoner=None):
        server_id = ctx.message.guild.id
        user_id = ctx.author.id
        regions = ['euw', 'br', 'na', 'eune', 'jp', 'las', 'lan', 'oce', 'tr', 'kr', 'ru']
        
        DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"
        PatchesData = urllib.request.urlopen(DataDragonUrl).read()
        Patches = json.loads(PatchesData)
        CurrentPatch = Patches[0]

        if region is None and summoner is None:
            await ctx.send("Please give me a region and a summoner!")
        elif region.lower() not in regions:
            await ctx.send("Please give me a valid region!")  
        elif summoner is None:
            await ctx.send("Please give me a summoner's name!") 
        else:   
            try:
                connection = pymysql.connect(
                    host=host,
                    database=database,
                    user=user,
                    password=password,
                    port=port)
                
                cur = connection.cursor()
                cur.execute(f"""SELECT * FROM profile WHERE server = '{server_id}' AND user_id = '{user_id}'""")
                data = cur.fetchone()
                if data is not None:
                    await ctx.send("You already have a summoner added to your account!") 
                else:
                    cur.execute(f"""INSERT INTO profile(server, user_id, region, summoner)
                                VALUES ('{server_id}', '{user_id}', '{region}', '{summoner}')""")
                    connection.commit()
                    cur.close()
                    
                    servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
                    for k,v in servers.items():
                        if region.lower() == k:
                            server = v

                    person = watcher.summoner.by_name(server, summoner)
                    Icon = person['profileIconId']
                
                    embed=discord.Embed(title=f'Added!', description="This summoner has been added to your account.", color=0xfda5b0)
                    embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/img/profileicon/{Icon}.png')
                    embed.set_author(name=f'{summoner} [{region.upper()}]')
                    await ctx.send(embed=embed)
            except pymysql.connect.Error as err:
                print("Something went wrong: {}".format(err))
            else:
                if connection is not None:
                    connection.close()

    @commands.command()
    async def remove(self, ctx):
        server_id = ctx.message.guild.id
        user_id = ctx.author.id
        try:
            conn = pymysql.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port)
            
            cur = conn.cursor()
            cur.execute(f"""SELECT * FROM profile WHERE server = '{server_id}' AND user_id = '{user_id}'""")
            data = cur.fetchone()
            if data is None:
                await ctx.send("You don't have a summoner added to your account.")
            else:
                profile_data = list(data)
                region = profile_data[1]
                summoner = profile_data[2]
                embed=discord.Embed(title=f'Removed', description=f"**{summoner} [{region.upper()}] has been removed from your account!** \n \u200B \n To link a new summoner, use the `y- add` command.", color=0xfda5b0)
                await ctx.send(embed=embed)
                cur.execute(f"""DELETE FROM profile WHERE server = '{server_id}' AND user_id = '{user_id}'""")
                conn.commit()
                cur.close()
        except pymysql.connect.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            if conn is not None:
                conn.close()

    @commands.command()
    async def leaderboard(self, ctx):
        server_id = ctx.message.guild.id
        user_id = ctx.author.id
        try:
            conn = pymysql.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port)
            
            cur = conn.cursor()
            cur.execute(f"""SELECT * FROM profile WHERE server = '{server_id}'""")
            data = cur.fetchall()
            if data is None:
                await ctx.send("There are no summoners added.")
            else:
                print(data)
                users = []
                regions = []
                summoners = []
                for x in range(len(data)):
                    print(data[x][0])
                    if (int(data[x][0])==int(server_id)):
                        print("True")
                        users.append(data[x][1])
                        regions.append(data[x][2])
                        summoners.append(data[x][3])
                

                DataDragonUrl = "https://ddragon.leagueoflegends.com/api/versions.json"

                server = []
                servers = {'euw':'euw1','br':'br1', 'na':'na1', 'eune':'eun1', 'jp':'jp1', 'las':'la2', 'lan':'la1', 'oce':'oc1', 'tr':'tr1', 'kr':'kr', 'ru':'ru'}
                for x in range(len(regions)):
                    for k,v in servers.items():
                        if regions[x].lower() == k:
                            server.append(v)
                print(server)

                summonerName = []
                SummonerID = []
                tier = []
                rank = []
                lp = []
                for x in range(len(users)):
                    person = watcher.summoner.by_name(server[x], summoners[x])
                    summonerName.append(person['name'])
                    SummonerID.append(person['id'])
                    stats = watcher.league.by_summoner(server[x], SummonerID[x])

                    res = None
                    for sub in stats:
                        if sub['queueType'] == "RANKED_SOLO_5x5":
                            res = sub
                            break 
                    n = stats.index(res)
                    tier.append(stats[n]['tier'])
                    rank.append(stats[n]['rank'])
                    lp.append(stats[n]['leaguePoints'])

                tiers = {'CHALLENGER':'1','GRANDMASTER':'2', 'MASTER':'3', 'DIAMOND':'4', 'PLATINUM':'5', 'GOLD':'6', 'SILVER':'7', 'BRONZE':'8', 'IRON':'9'}
                ranks = {'I':'1','II':'2','III':'3','IV':'4'}
                tierprintformat = {'Challenger':'1','Grandmaster':'2', 'Master':'3', 'Diamond':'4', 'Platinum':'5', 'Gold':'6', 'Silver':'7', 'Bronze':'8', 'Iron':'9'}

                tier_number = []
                rank_number = []
                for x in range(len(tier)):
                    for k,v in tiers.items():
                        if tier[x] == k:
                            tier_number.append(v)
                    for k,v in ranks.items():
                        if rank[x] == k:
                            rank_number.append(v)

                print(tier_number) 
                print(rank_number)

                keys = [summonerName, tier, rank, lp]
                order = []
                for x in range(len(data)):
                    order.append([summonerName[x],tier_number[x],rank_number[x],lp[x]])

                ordered = sorted(order, key=itemgetter(1,2,3))
                print(order)
                print(ordered)

                for i in range(len(ordered)):
                    print("")

                for i in range(len(ordered)):
                    for k,v in tierprintformat.items():
                        if ordered[i][1] == v:
                            ordered[i][1] = k
                    for k,v in ranks.items():
                        if ordered[i][2] == v:
                            ordered[i][2] = k

                embed = discord.Embed(
                    title = f"***LEADERBOARD***", 
                    colour = 16742893
                )

                masteryembeds = []
                if (len(ordered) > 50):
                    leaderboardlength = 50
                else:
                    leaderboardlength = len(ordered)
                for i in range(math.ceil(leaderboardlength/10)):
                    masteryembeds.clear()
                    text = None
                    for j in range(10):
                        try:
                            masteryembeds.append(f'**[{i*10+j+1}]** *{ordered[10*i+j][0]}* in {ordered[10*i+j][1]} {ordered[10*i+j][2]} with {ordered[10*i+j][3]} LP')
                        except:
                            pass
                        nl = '\n'
                        text = f"{nl}{nl.join(masteryembeds)}"
                    print(text)
                    embed.add_field(name=f'Top {(i + 1) * 10}', value = f'{text}', inline=False)
                
                await ctx.send(embed=embed)

        except pymysql.connect.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            if conn is not None:
                conn.close()


def setup(client):
    client.add_cog(Leaderboard(client))