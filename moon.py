# @DwyteMartin on Twitter

import discord
from datetime import datetime, timedelta
import time
import requests
import asyncio
import configparser as cfg

client = discord.Client()
loop = asyncio.get_event_loop()

moon_bot = None

class MoonBot():
    def __init__(self, channel):
        self.channel = channel

        # Send and Sets self.message
        loop.create_task(self.send_message())

    async def clean_channel(self):
        async for message in self.channel.history():
            if message.author == client.user:
                await message.delete()

    async def send_message(self):
        await self.clean_channel()

        self.message = await self.channel.send(self.get_moon_message())

        # Start Real Time Update Recursion
        loop.call_later(60, self.update_live)

    def update_live(self):
        loop.create_task(self.update_message())
        loop.call_later(60, self.update_live)
        
    async def update_message(self):
        await self.message.edit(content=self.get_moon_message())

    def get_moon_emoji(self):
        now = getDateNow()
        year = now.year
        month = now.month
        day = now.day

        c = 365.25 * year

        e = 30.6 * month

        # jd is total days elapsed
        jd = c + e + day - 694039.09

        # divide by the moon cycle
        jd /= 29.5305882

        # int(jd) -> b, take integer part of jd
        b = int(jd)

        # subtract integer part to leave fractional part of original jd
        jd -= b

        b = round(jd * 8)

        # 0 and 8 are the same so turn 8 into 0
        if (b >= 8):
            b = 0

        moon_phase = ""

        if b == 0:
            moon_phase = ":new_moon:"
        elif b == 1:
            moon_phase = ":waxing_crescent_moon:"
        elif b == 2:
            moon_phase = ":first_quarter_moon:"
        elif b == 3:
            moon_phase = ":waxing_gibbous_moon:"
        elif b == 4:
            moon_phase = ":full_moon:"
        elif b == 5:
            moon_phase = ":waning_gibbous_moon:"
        elif b == 6:
            moon_phase = ":last_quarter_moon:"
        elif b == 7:
            moon_phase = ":waning_crescent_moon:"
        else:
            return b

        return moon_phase

    def get_moon_message(self):
        full_moon = requests.get(
            "http://isitfullmoon.com/api.php?format=json").json()['isitfullmoon']

        full_moon_prev = datetime.fromtimestamp(full_moon['prev'])
        full_moon_date = datetime.fromtimestamp(full_moon['next'])

        full_moon_status = "{}".format(self.getDeltaStr(getDateNow(), full_moon_date)) if full_moon['status'] == "No" else "Yep, it's currently full moon."

        output = ">>> "
        output += "{} **{}**".format(self.get_moon_emoji(), full_moon_status)
        output += "```yaml\nPrev: {}\n".format(
            full_moon_prev.strftime("%b %d, %Y (%a)"))
        output += "Next: {}```".format(
            full_moon_date.strftime("%b %d, %Y (%a)"))

        return output

    def getDeltaStr(self, datetimeFrom, datetimeTo):
        delta = datetimeTo - datetimeFrom

        if delta.total_seconds() <= 0:
            return "Occured @ {}".format(str(datetimeTo.date()))
        
        output = "In "

        days = delta.days
        week = days // 7
        if week > 0:
            output += "{} week{} ".format(week, "s" if week > 1 else "")

            days = days % 7

        if days > 0:
            output += "{} day{} ".format(days, "s" if days > 1 else "")
            
        hours, rem = divmod(delta.seconds, 3600)
        if hours > 0:
            output += "{} hour{} ".format(hours, "s" if hours > 1 else "")

        minutes, seconds = divmod(rem, 60)
        if minutes > 0:
            output += "{} minute{} ".format(minutes, "s" if minutes > 1 else "")

        return output

def getDateNow():
    return datetime.now()

def parse_config(field):
    parser = cfg.ConfigParser()
    parser.read("config.cfg")
    return parser.get('token_ids', field)

@client.event
async def on_ready():
    ''' Called when bot is ready.'''
    global moon_bot

    print('Logged in as', client.user.name)
    print('------')

    channel_id = int(parse_config("channel_id"))
    moon_channel = client.get_channel(channel_id)
    moon_bot = MoonBot(moon_channel)

def main():
    # Start Asyncio loop of the client starting.
    try:
        loop.run_until_complete(client.start(parse_config("bot_token")))
    finally:
        loop.close()

if __name__ == '__main__':
    main()
