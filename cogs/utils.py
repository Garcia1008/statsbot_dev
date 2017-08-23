from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import textwrap
from contextlib import redirect_stdout
import io
import datetime
import random


class Utility:

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send('Shutting down...')
        self.bot.session.close()
        await self.bot.logout()

    @commands.command()
    async def info(self, ctx, *, arg : str = None):
        uptime = (datetime.datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time_ = '%s days, %s hours, %s minutes, and %s seconds' % (days, hours, minutes, seconds)
        else:
            time_ = '%s hours, %s minutes, and %s seconds' % (hours, minutes, seconds)
        servers = len(self.bot.guilds)
        version = '3.0.0'
        library = '[discord.py](http://discordpy.readthedocs.io/en/rewrite/)'
        creator = '[verixx](https://discord.gg/pmQSbAd), [tryso](https://discord.gg/5TRPdBr) & [Harmiox](https://discord.gg/j3wJgm7)'
        users = 0
        for server in self.bot.guilds:
            users += len(server.members)
        invite = '[Click Here]({})'.format(self.make_invite())
        discord_ = '[Click Here](https://discord.gg/j3wJgm7)'
        github = '[verixx/statsbot](https://github.com/verixx/statsbot)'
        time = ctx.message.created_at
        emb = discord.Embed(color=random.randint(0x000000,0x00ffff))
        emb.set_author(name='Stats - Info', icon_url=self.bot.user.avatar_url)
        emb.add_field(name='Version',value=version)
        emb.add_field(name='Library',value=library)
        emb.add_field(name='Developers',value=creator)
        emb.add_field(name='Invite',value=invite)
        emb.add_field(name='Github',value=github)
        emb.add_field(name='Support Server',value=discord_)
        emb.add_field(name='Servers',value=servers)
        emb.add_field(name='Users',value=users)
        emb.add_field(name='Uptime',value=time_)
        emb.set_footer(text="ID: {} | Powered by node-cr-proxy".format(self.bot.user.id))
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)


    @commands.command()
    async def help(self, ctx):
        p = ctx.prefix
        em = discord.Embed(color=random.randint(0x000000,0x00ffff))
        em.set_author(name='Stats - Help',icon_url='https://i.imgur.com/ydkZsVI.png')
        em.set_thumbnail(url='https://i.imgur.com/ydkZsVI.png')
        em.add_field(name='{}profile'.format(p),value='View player info, stats, deck, chests and much more!',inline=False)
        em.add_field(name='{}save'.format(p),value='Save your tag to your discord profile.',inline=False)
        em.add_field(name='{}stats'.format(p),value='View basic player statistics.',inline=False)
        em.add_field(name='{}clan'.format(p),value='View clan information.',inline=False)
        em.add_field(name='{}chests'.format(p),value='See your basic chest cycle and upcoming chests.',inline=False)
        em.add_field(name='{}offers'.format(p),value='See your shop offers',inline=False)
        em.add_field(name='{}deck'.format(p),value='See your current battle deck.',inline=False)
        em.add_field(name='{}info'.format(p),value='See info about the bot.',inline=False)
        em.set_footer(text='Stats v3.0')
        await ctx.send(embed=em)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, cog):
        module = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(module)
            msg = await ctx.send('Successfully Unloaded.')
            self.bot.load_extension(module)
            await msg.edit(content='Successfully Reloaded.')
        except Exception as e:
            await msg.edit(content='\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await msg.edit(content='Done. \N{OK HAND SIGN}')


    @commands.command()
    async def ping(self, ctx):
        """Pong! Check your response time."""
        msgtime = ctx.message.created_at
        now = datetime.datetime.now()
        ping = now - msgtime
        pong = discord.Embed(title='Pong! Response Time:',
                             description=str(ping.microseconds / 1000.0) + ' ms',
                             color=0x00ffff)

        await ctx.send(embed=pong)

    @commands.command(aliases=['invite'])
    async def join(self, ctx):
        """Joins a server."""
        await ctx.send('**Invite Link**\n<{}>'.format(self.make_invite()))

    def make_invite(self):
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.external_emojis = True
        perms.send_messages = True
        perms.embed_links = True
        return discord.utils.oauth_url(self.bot.client_id, perms)



    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    @commands.command(name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('```py\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send('```py\n%s\n```' % value)
            else:
                self._last_result = ret
                await ctx.send('```py\n%s%s\n```' % (value, ret))

 

def setup(bot):
    bot.add_cog(Utility(bot))
