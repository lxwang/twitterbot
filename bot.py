import discord
from discord.ext import commands, tasks
import os
import datetime
from pytz import timezone
import json
import asyncio

import stream
from discord_tokens import twitterbot_token

channel_list = [664757315714416664, 801541146668564521]

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    get_tweet.start()
    await stream.start_stream()
    

@tasks.loop(seconds= 5)
async def get_tweet():
    channel = bot.get_channel(664757315714416664)

    while True:
        newtweet = stream.get_tweet()
        if newtweet:
            for i in channel_list:
                try:
                    channel = bot.get_channel(i)
                    await channel.send(newtweet)
                except:
                    pass

        await asyncio.sleep(5)

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def followlist(ctx):
    print("listing")
    await ctx.send(", ".join(stream.follow_list))

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def follow(ctx, msg: str):
    #if user.display_name in mod_list or user.id in mod_list:
    #    return

    # command to add account to follow
    s = stream.addfollow(msg)
    if s:
        await ctx.send("Following {}".format(msg))

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def unfollow(ctx, msg: str):
    #if user.display_name in mod_list or user.id in mod_list:
    #    return

    # command to add account to follow
    s = stream.unfollow(msg)
    if s:
        await ctx.send("Unfollowed {}".format(msg))

bot.run(twitterbot_token)

