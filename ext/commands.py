import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands

from utility import Config

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name="close", with_app_command=True, description="Close a Help-Thread")
    @commands.guild_only()
    async def close_command(self, ctx: commands.Context, reason: Optional[str]):
        return
        await ctx.send("Dieser Kanal ist kein Hilfe-Thread.", delete_after=3, ephemeral=True)
    
    @app_commands.command(name="set_help_channel", description="Set the Help-Channel")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def help_channel_command(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        conf = Config().get()
        
        _chn = self.bot.get_channel(int(channel.id))
        
        if not isinstance(_chn, discord.ForumChannel):
            await interaction.response.send_message("Das ist keine Forum-Kanal.", ephemeral=True)
        
        conf["help_channel"] = channel.id
        Config().save(conf)
        
        await interaction.response.send_message(f"Help-Channel zu `{_chn.name}` gesetzt.", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")