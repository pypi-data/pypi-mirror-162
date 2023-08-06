import disnake
from disnake.ext import commands
import datetime
from luawhitelist import luawl

def Bot(admins: list, token: str, prefix: str = None, help_command: bool = None):
    prefix = prefix or '!'
    admins = admins
    token = token

    bot = commands.Bot(command_prefix=prefix, help_command=help_command, intents=disnake.Intents.all())

    @bot.event
    async def on_ready():
        print(bot.user, 'Ready')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            embed = modify_embed(title = 'You do not have the required permissions', colour = disnake.Colour.brand_red())
            await ctx.send(embed = embed)
        else:
            pass

    @bot.event
    async def on_slash_command_error(inter, error):
        if isinstance(error, commands.errors.CheckFailure):
            embed = modify_embed(title = 'You do not have the required permissions', colour = disnake.Colour.brand_red())
            await inter.send(embed = embed)
        else:
            pass

    def modify_embed(*args, **kwargs) -> disnake.Embed:
        embed = disnake.Embed(*args, **kwargs)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'luaWhitelist {bot.user.name}')
        return embed

    def owner_or_admin():
        def predicate(ctx):
            return ctx.author.id in admins

        return commands.check(predicate)

    @bot.slash_command(description="Add user whitelist")
    @owner_or_admin()
    async def whitelist_add(interaction, user: disnake.User):
        result = luawl.whitelist_add(discord_id = user.id, expire_timestamp = 0)

        if result.get("message") == "whitelist already":
            embed = modify_embed(title = 'Already whitelisted')
            embed.colour = disnake.Colour.yellow()
            return await interaction.send(embed = embed)    

        if result.get("message") == "whitelist add" and not interaction.author.id == bot.owner_id:
            embed = modify_embed(title = 'Add whitelist successfully', colour = disnake.Colour.brand_green())
            embed.description = f'{user} added whitelist'
            await interaction.send(embed = embed) 

        if result.get('key') and result.get("message") == "whitelist add":
            embed = modify_embed(title = f"{interaction.author} added you whitelist", colour = disnake.Colour.brand_green())
            embed.description = f'```lua\ngame:HttpGet("{luawl.url}premium/auth/{result["key"]}/"..game:GetService("RbxAnalyticsService"):GetClientId()) ```'

            return await user.send(embed = embed)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.send(embed = embed)

    @bot.slash_command(interaction="Delete user whitelist")
    @owner_or_admin()
    async def whitelist_del(interaction, user: disnake.User):
        result = luawl.whitelist_del(discord_id = user.id)
        
        if result.get('status') == 200:
            embed = modify_embed(title = f'Successfully whitelisted deleted {user}', colour = disnake.Colour.brand_green())
            return await interaction.send(embed = embed)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.send(embed = embed)

    @bot.slash_command(description="Get your script key")
    async def getkey(interaction):
        result = luawl.info(discord_id = interaction.author.id)

        if result.get('status') == 200 and result.get('key'):
            embed = modify_embed(colour = disnake.Colour.brand_green())
            embed.add_field(name = 'Whitelist Key:', value = result.get('key'), inline = False)
            return await interaction.send(embed = embed, ephemeral = True)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.send(embed = embed)

    @bot.slash_command(description="Get your script for login system")
    async def authscript(interaction):
        result = luawl.info(discord_id = interaction.author.id)

        if result.get('status') == 200 and result.get('key'):
            embed = modify_embed(title = f"{interaction.author} added you whitelist", colour = disnake.Colour.brand_green())
            embed.description = f'```lua\ngame:HttpGet("{luawl.url}premium/auth/{result["key"]}/"..game:GetService("RbxAnalyticsService"):GetClientId()) ```'

            return await interaction.send(embed = embed, ephemeral = True)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.send(embed = embed)

    @bot.slash_command(description="Reset your key")
    async def resetkey(interaction):
        result = luawl.reset_key(discord_id = interaction.author.id)

        if result.get('status') == 200:
            embed = modify_embed(title = 'Successfully reset key', colour = disnake.Colour.brand_green())
            return await interaction.send(embed = embed)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.send(embed = embed)

    @bot.slash_command(description="Reset your hwid")
    async def resethwid(interaction):
        result = luawl.reset_hwid(discord_id = interaction.author.id)

        if result.get('status') == 200:
            embed = modify_embed(title = 'Successfully reset hwid', colour = disnake.Colour.brand_green())
            return await interaction.send(embed = embed)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.send(embed = embed)

    @bot.slash_command(description="Get information about the user")
    @owner_or_admin()
    async def info(interaction, user: disnake.User):
        result = luawl.info(discord_id = user.id)

        if result.get('status') == 200:
            embed = modify_embed(colour = disnake.Colour.brand_green())
            result.pop('hwid')
            for name, value in result.items():
                embed.add_field(name = name, value = value, inline = False)
            return await interaction.send(embed = embed, ephemeral = True)

        embed = modify_embed(title = f'Error: Request failed with status code {result.get("status")}', colour = disnake.Colour.brand_red())
        return await interaction.edit_original_message(embed = embed)

    bot.run(token)

