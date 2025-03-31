import discord
from discord.ext import commands

# Define the intents
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='m!', intents=intents)

# STATUS ONLINE
@client.event
async def on_ready():
    print('Initializing Bot')
    print('Commands Enabled')
    print('Bot Online YES')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Moe_Gamers Island"))
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))

# MODERATION MODULE

# SLOWMODE
@client.command()
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")

# DEAFEN
@client.command()
async def DEAFEN(ctx, usr: discord.Member):
    await usr.edit(deafen=True)

# Undeafen
@client.command()
@commands.has_role("813318017265434644")
async def UN_DEAFEN(ctx, usr: discord.Member):
    await usr.edit(deafen=False)

# LOCK
@client.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(ctx.channel.mention + " ***is now locked.***")

# UNLOCK
@client.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(ctx.channel.mention + " ***has been unlocked.***")

# MUTE
@client.command(description="Mutes the specified user.")
@commands.has_permissions(manage_messages=True)
async def MUTE(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True,
                                          read_messages=False)
    embed = discord.Embed(title="muted", description=f"{member.mention} was muted", colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f"You have been muted from: {guild.name} reason: {reason}")

# UNMUTE
@client.command(description="Unmutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def UN_MUTE(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    await member.send(f"You have been unmuted from: {ctx.guild.name}")
    embed = discord.Embed(title="unmute", description=f"Unmuted {member.mention}", colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)

# BAN
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if not member:
        await ctx.send('Please mention a member')
        return
    await member.ban()
    await ctx.send(f'{member.display_name} was banned from the server')

# BAN ERROR
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You are not allowed to use this command!")

# ERROR OF NOT OWNER OF BOT
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send('You are not the owner of the bot')

# DM-WARN
@client.command()
async def DM_WARN(ctx, member: discord.Member, *, messagetosend):
    await member.send(messagetosend)
    await ctx.send(f'Message sent to {member.name}!')

# DM
@client.command()
async def DM(ctx, member: discord.Member, *, messagetosend):
    await member.send(messagetosend)
    await ctx.send(f'Message sent to {member.name}!')

# UNBAN VIA USER ID
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user):
    user = await client.fetch_user(user)
    await ctx.guild.unban(user)
    await ctx.send(f'Unbanned {user.name}')

# UNBAN ERROR VIA USER ID
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You are not allowed to use this command!")

# NUMBER OF USERS
@client.command(aliases=["mc"])
async def member_count(ctx):
    a = ctx.guild.member_count
    b = discord.Embed(title=f"Members in {ctx.guild.name}", description=a, color=discord.Color((0xffff00)))
    await ctx.send(embed=b)

# KICK
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if not member:
        await ctx.send('Please mention a member')
        return
    await member.kick()
    await ctx.send(f'{member.display_name} was kicked from the server')

# MANAGER MODULE

# PURGE
@client.command(pass_context=True)
async def purge(ctx, amount=30):
    channel = ctx.message.channel
    messages = []
    async for message in channel.history(limit=amount + 1):
        messages.append(message)

    await channel.delete_messages(messages)
    await ctx.send(f'{amount} messages have been purged by {ctx.message.author.mention}')

@client.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.logout()

# CLIENT INFO
client.run('**************************************************')
