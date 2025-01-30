import os

import discord
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

intents = discord.Intents.all()

activity = discord.Activity(type=discord.ActivityType.watching, name="your threads")

bot = discord.Bot(intents=intents, activity=activity, status=discord.Status.idle)

# №1 - Owner, №2 - Admin
admin_roles = [1327291755103781001, 1327291755103781000]

russian_role = 1327293778029056072
english_role = 1327293796702224466


@bot.listen(once=True)
async def on_ready():
    logger.info(f"bluetooth device is ready to pair")


@bot.slash_command(name="close", description="Close forum thread")
async def close(ctx: discord.ApplicationContext):
    if any(role.id in admin_roles for role in ctx.author.roles):
        logger.debug(f"close command executed")
        thread = bot.get_channel(ctx.channel_id)

        await thread.edit(name=f"{thread.name} (CLOSED)")

        await ctx.respond(f"Thread closed")
        await thread.edit(locked=True)
        await thread.archive()


@bot.slash_command(name="added", description="Mark forum thread as added")
async def add(ctx: discord.ApplicationContext):
    if any(role.id in admin_roles for role in ctx.author.roles):
        logger.debug(f"added command executed")
        thread = bot.get_channel(ctx.channel_id)

        await thread.edit(name=f"{thread.name} (ADDED)")
        await thread.archive()
        await ctx.send(f"Thread marked as added")


class ThreadConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if any(role.id in admin_roles for role in interaction.user.roles):
            await bot.get_channel(interaction.channel_id).delete()
            self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if any(role.id in admin_roles for role in interaction.user.roles):
            await interaction.response.send_message(
                "Operation cancelled", ephemeral=True
            )
            self.stop()


@bot.slash_command(name="remove", description="Remove forum thread")
async def remove(ctx: discord.ApplicationContext):
    if any(role.id in admin_roles for role in ctx.author.roles):
        logger.debug(f"confirm command executed")

        embed = discord.Embed(
            title="Confirmation",
            description="Are you sure you want to proceed?",
            color=discord.Color.blue(),
        )
        view = ThreadConfirmView()
        await ctx.send(embed=embed, view=view)


@bot.listen()
async def on_thread_create(thread: discord.Thread):
    message = await thread.fetch_message(thread.id)
    
    if any(role.id == russian_role for role in thread.owner.roles):
        if any(not attach.filename.endswith(".dll") for attach in message.attachments):
            await thread.send("Мы принимаем только файлы с расширением .dll\nАдминистратор будет уведомлен о вашем сообщении")
            await thread.send(f"<@&{admin_roles[1]}>")
    else:
        if any(not attach.filename.endswith(".dll") for attach in message.attachments):
            await thread.send("We only accept files with .dll extension\nAn admin will be notified about your message")
            await thread.send(f"<@&{admin_roles[1]}>")

bot.run(os.getenv("TOKEN"))
