import discord
from discord.ext import commands
from ext.formatter import EmbedHelp
import datetime
import aiohttp

class StatsBot(commands.AutoShardedBot):

    def __init__(self):

        super().__init__(command_prefix='#')

        self.client_id = 347006499677143041
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.token = open('data/bot_token').read()
        self.remove_command('help')
        self._extensions = ['stats','utils']

        for extension in self._extensions:
            try:
                self.load_extension('cogs.'+extension)
                print('Loaded ext: {}'.format(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed ext: {}\n{}'.format(extension, exc))

    def run(self):
        super().run(self.token, reconnect=True)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.now()

        print('-------')
        print('StatsBot Online!')
        print('-------')
        print('ID: {}'.format(self.user.id))

    async def on_resume(self):
        print('-------')
        print('StatsBot Resumed')
        print('-------')

    async def on_shard_ready(self, shard_id):
        self.shard_id = shard_id
        print('Shard `{}` ready.'.format(shard_id))

if __name__ == '__main__':
    bot = StatsBot()
    bot.run()
