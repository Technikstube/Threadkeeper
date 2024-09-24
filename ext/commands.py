import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands

from utility import Config, Thread

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def close_thread(self, thread: discord.Thread):
        closed_embed = discord.Embed(
                title="",
                description="Dieser Thread ist nun geschlossen. Sollte deine Frage / dein Problem weiterhin bestehen kannst du gerne einen neuen Thread erstellen!",
                color=discord.Color.orange()
            )
        closed_embed.set_author(name="Hilfe-Thread geschlossen", icon_url=self.bot.user.avatar.url)
        await thread.send(embed=closed_embed)
        await thread.edit(name=f"🔒 {thread.name}", archived=True, locked=True)

    @commands.hybrid_command(name="close", with_app_command=True, description="Close a Help-Thread")
    @commands.guild_only()
    async def close_command(self, ctx: commands.Context, reason: Optional[str]):
        threads = Thread().get()
        conf = Config().get()
        forum = None
        target = None
        
        if "help_channel" in conf:
            forum: discord.ForumChannel = self.bot.get_channel(int(conf["help_channel"]))
        
        if forum is None:
            await ctx.send("Ich habe kein Hilfeforum gefunden. (`/set_help_channel`)", delete_after=5, ephemeral=True)
            return
        
        for _thread in forum.threads:
            if _thread.id == ctx.channel.id:
                target: discord.Thread = _thread
                break
    
        if target is None:
            await ctx.send("Dieser Kanal ist kein Hilfe-Thread.", delete_after=3, ephemeral=True)
            return
        elif str(target.id) not in threads:
            await ctx.send("Dieser Thread ist kein Hilfe-Thread.", delete_after=3, ephemeral=True)
            return
        elif target.locked:
            threads.pop(str(target.id))
            Thread().save(threads)
            await ctx.send("Dieser Thread ist kein Hilfe-Thread.", delete_after=3, ephemeral=True)
            return
        elif target.flags.pinned:
            threads.pop(str(target.id))
            Thread().save(threads)
            await ctx.send("Dieser Thread ist angepinnt.", delete_after=3, ephemeral=True)
            return
    
        await self.close_thread(target)
        threads.pop(str(target.id))
        Thread().save(threads)
        
    @app_commands.command(name="set_help_channel", description="Set the Help-Channel")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def help_channel_command(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        conf = Config().get()
        
        _chn = self.bot.get_channel(int(channel.id))
        
        if not isinstance(_chn, discord.ForumChannel):
            await interaction.response.send_message("Ungültiger Kanaltyp. (Nur Forumkanäle)", ephemeral=True)
        
        conf["help_channel"] = channel.id
        Config().save(conf)
        
        await interaction.response.send_message(f"Hilfekanal gesetzt. ({_chn.mention})", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")