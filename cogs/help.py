import discord
from discord.ext import commands

class Help(commands.Cog):
    """Sends this help message"""

    def __init__(self, init):
        self.init = init

    @commands.command()
    async def help(self, ctx, *input):
        """Shows all modules of that bot"""
	
        prefix = "y- "

        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:

            # starting to build embed
            emb = discord.Embed(title='Commands for YUUMI Bot', color=16742893,
                                description=f'Use `{prefix}help <module>` to gain more information about that module ')
            
            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.init.cogs:
                cogs_desc += f'`{cog}` {self.init.cogs[cog].__doc__}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.init.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:

            # iterating trough cogs
            for cog in self.init.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commands', description=self.init.cogs[cog].__doc__,
                                        color=16742893)

                    # getting commands from cog
                    for command in self.init.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard from a module called `{input[0]}` before :scream:",
                                    color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module at once :sweat_smile:",
                                color=discord.Color.orange())

        # send embed
        emb.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/Yuumi_11.jpg')
        await ctx.send(embed=emb)


def setup(client):
    client.add_cog(Help(client))
