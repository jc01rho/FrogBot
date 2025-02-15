# modules.reactions.welcome

from disnake.ext import commands
import asyncio
import random
import json

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gif_links = ["https://cdn3.emoji.gg/emojis/1463-wave.gif"] * 49 + \
                         ["https://i.pinimg.com/originals/ab/bd/b6/abbdb6e66ec39dc9262abc617fbc2b02.gif"] * 49 + \
                         ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYzhsN3Fnd2c1MG1hcmhwMG00czE5ZHZoZmZsa3k4N3hqcWJya2NwdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5xtDarIELDLO7lSFQJi/giphy.gif"]

    def load_state(self):
        try:
            with open('state.json', 'r') as f:
                state = json.load(f)
                return state.get('non_successful_spawns', 0)
        except FileNotFoundError:
            return 0

    def save_state(self, non_successful_spawns):
        try:
            with open('state.json', 'w') as f:
                json.dump({'non_successful_spawns': non_successful_spawns}, f)
        except Exception as e:
            print(f"Failed to save state: {e}")

    async def send_welcome_message(self, channel, member, gif=None):
        try:
            await channel.send(f"Hello {member.mention}! If you need anything just ask!")
            if gif:
                await channel.send(gif)
        except Exception as e:
            print(f"Failed to send welcome message or gif: {e}")
            await asyncio.sleep(10)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = member.guild.system_channel
        if welcome_channel:
            await asyncio.sleep(5)
            non_successful_spawns = self.load_state()
            for _ in range(20):
                selected_gif = random.choice(self.gif_links)
                if random.random() < 0.05 + non_successful_spawns * 0.05:
                    await self.send_welcome_message(welcome_channel, member, selected_gif)
                    break
                non_successful_spawns += 1
                self.save_state(non_successful_spawns)
            else:
                await self.send_welcome_message(welcome_channel, member)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))