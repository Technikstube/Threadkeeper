import discord
import os
import sys
import asyncio
import signal
import random
from dotenv import get_key
from datetime import datetime
from discord.ext import commands, tasks

from utility import Thread, Config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

MAXIMUM_INACTIVITY_SECONDS = 1 # 129600 # 36 hours in seconds

class TSHelper(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            help_command=None,
            intents=intents
        )
        
    async def close_thread(self, thread: discord.Thread):
        closed_embed = discord.Embed(
                title="",
                description="Dieser Thread ist nun geschlossen. Sollte deine Frage / dein Problem weiterhin bestehen kannst du gerne einen neuen Thread erstellen!",
                color=discord.Color.orange()
            )
        closed_embed.set_author(name="Hilfe-Thread geschlossen", icon_url=self.user.avatar.url)
        await thread.send(embed=closed_embed)
        await thread.edit(name=f"🔒 {thread.name}", archived=True, locked=True)

    @tasks.loop(minutes=2)
    async def thread_archiver(self):
        THREADS = Thread().get()
        threads = Thread().get()
        
        await self.thread_scanner()
        
        for _thread in THREADS:
            dist = round(datetime.now().timestamp()) - round(THREADS[str(_thread)]["last_activity"])
            if dist >= MAXIMUM_INACTIVITY_SECONDS:
                thread: discord.Thread = self.get_channel(int(_thread))
                if thread.flags.pinned:
                    threads.pop(_thread)
                    Thread().save(threads)
                    continue
                await self.close_thread(thread)
                threads.pop(_thread)
                Thread().save(threads)
                await asyncio.sleep(0.2)
                
    async def thread_scanner(self):
        threads = Thread().get()
        conf = Config().get()
        forum = None
        
        if "help_channel" in conf:
            forum: discord.ForumChannel = self.get_channel(int(conf["help_channel"]))
        
        if forum is not None:
            for _thread in forum.threads:
                last_message = None
                await asyncio.sleep(0.2)
                if str(_thread.id) in threads:
                    continue
                if _thread.locked:
                    continue
                if _thread.flags.pinned:
                    continue
                
                try:
                    if await _thread.fetch_message(_thread.starter_message.id) is not None:
                        message: discord.Message = await _thread.fetch_message(_thread.id)
                        last_message = message.created_at.timestamp()
                except:
                    pass
                try:
                    if await _thread.fetch_message(_thread.last_message_id) is not None:
                        message: discord.Message = await _thread.fetch_message(_thread.last_message_id)
                        last_message = message.created_at.timestamp()
                except:
                    pass
                if last_message is None:
                    print("none")
                    await self.close_thread(_thread)
                    continue
                dist = round(datetime.now().timestamp()) - round(last_message)
                if dist >= MAXIMUM_INACTIVITY_SECONDS:
                    await self.close_thread(_thread)
                    continue
                threads[str(_thread.id)] = {
                "last_activity": last_message
                }
                Thread().save(threads)
                
        
    @tasks.loop(minutes=60.1)
    async def presence_tick(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.Activity(
                type=discord.ActivityType.watching, name="Technikstube"
            ),
            discord.Activity(
                type=discord.ActivityType.watching, name="Tech-Support"
            ),
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.online
        )

    async def setup_hook(self):
        pass
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\\_(ツ)_/¯")
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.dnd
        )
    
    async def on_ready(self):
        
        self.presence_tick.start()
        self.thread_archiver.start()
        
        for path in paths:
            for file in os.listdir(path):
                if file.startswith("-"):
                    continue
                if file.endswith(".py"):
                    await self.load_extension(f"{path.replace("/", ".")}{file[:-3]}")
    
        sync = await self.tree.sync()
        print(f"> Synced {len(sync)} commands")
    
        print(
            f">> {self.user.name} Ready"
            )

# Shutdown Handler
def shutdown_handler(signum, frame):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(TSHelper().logout())
    # Cancel all tasks lingering
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    loop.close()

    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

bot = TSHelper()

bot.run(os.environ.get("TOKEN", get_key("./.env", "TOKEN")))
