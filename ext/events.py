import discord
from datetime import datetime
from discord.ext import commands

from utility import Config, Thread

new_thread_description = """
- **Stelle deine Frage**.
- **Erkläre was passiert ist**, was hast du davor gemacht? (Kürzlich Einstellungen geändert, Programme installiert?, usw.)
"""

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        
    @commands.Cog.listener(name="on_thread_create")
    async def on_thread_create(self, thread: discord.Thread):
        parent = None
        threads = Thread().get()
        conf = Config().get()
        
        if isinstance(thread.parent, discord.ForumChannel):
            parent: discord.ForumChannel = thread.parent
            
            if "help_channel" not in conf:
                return
            
            if int(conf["help_channel"]) != parent.id:
                return
            
            threads[str(thread.id)] = {
                "last_activity": datetime.now().timestamp()
            }
            Thread().save(threads)
            
            new_thread_embed = discord.Embed(
                title="",
                description=new_thread_description,
                color=discord.Color.brand_green()
            )
            new_thread_embed.set_author(name="Neuer Hilfe-Thread geöffnet", icon_url=self.bot.user.avatar.url)
            new_thread_embed.set_footer(text="Schließt sich automatisch nach Inaktivität oder mit !close")
            
            await thread.send(thread.owner.mention, embed=new_thread_embed)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        threads = Thread().get()
        
        if isinstance(message.channel, discord.Thread):
            if str(message.channel.id) in threads:
                threads[str(message.channel.id)]["last_activity"] = datetime.now().timestamp()
                Thread().save(threads)

        
async def setup(bot):
    await bot.add_cog(Events(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")