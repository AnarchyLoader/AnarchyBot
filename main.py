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

        new_name = thread.name
        if len(new_name) > 70:
            new_name = new_name[:70]
        await thread.edit(name=f"{new_name} (CLOSED)")

        embed = discord.Embed(
            title="Thread Closed",
            description="✅ Thread closed",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed)
        await thread.edit(locked=True)
        await thread.archive()


@bot.slash_command(name="added", description="Mark forum thread as added")
async def add(ctx: discord.ApplicationContext):
    if any(role.id in admin_roles for role in ctx.author.roles):
        logger.debug(f"added command executed")
        thread = bot.get_channel(ctx.channel_id)

        new_name = thread.name
        if len(new_name) > 70:
            new_name = new_name[:70]
        await thread.edit(name=f"{new_name} (ADDED)")
        await thread.archive()

        embed = discord.Embed(
            title="Thread Added",
            description="➕ Thread marked as added",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)


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
            description="⚠️ Are you sure you want to proceed?",
            color=discord.Color.blue(),
        )
        view = ThreadConfirmView()
        await ctx.send(embed=embed, view=view)


@bot.listen()
async def on_thread_create(thread: discord.Thread):
    if thread.parent_id == 1327295090456006697:
        message = await thread.fetch_message(thread.id)

        if any(role.id == russian_role for role in thread.owner.roles):
            if any(
                not attach.filename.endswith(".dll") for attach in message.attachments
            ):
                embed = discord.Embed(
                    title="File Extension Requirement",
                    description="Мы принимаем только файлы с расширением .dll\nАдминистратор будет уведомлен о вашем сообщении",
                    color=discord.Color.yellow(),
                )
                await thread.send(embed=embed)
                await thread.send(f"⚠️ <@&{admin_roles[1]}>")
        else:
            if any(
                not attach.filename.endswith(".dll") for attach in message.attachments
            ):
                embed = discord.Embed(
                    title="File Extension Requirement",
                    description="We only accept files with .dll extension\nAn admin will be notified about your message",
                    color=discord.Color.yellow(),
                )
                await thread.send(embed=embed)
                await thread.send(f"⚠️ <@&{admin_roles[1]}>")


@bot.slash_command(name="autoname", description="Automatically name the thread")
async def autoname(ctx: discord.ApplicationContext):
    thread = bot.get_channel(ctx.channel_id)

    message = await thread.fetch_message(thread.id)
    if message.attachments:
        filename = message.attachments[0].filename
        await thread.edit(name=filename)
        embed = discord.Embed(
            title="Thread Name Updated",
            description=f"✅ Thread name updated to {filename}",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(
            title="No Attachments",
            description="❌ No attachments found",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed)


@bot.slash_command(name="lock", description="Lock and archive the thread")
async def lock(ctx: discord.ApplicationContext):
    if any(role.id in admin_roles for role in ctx.author.roles):
        logger.debug(f"lock command executed")
        thread = bot.get_channel(ctx.channel_id)

        embed = discord.Embed(
            title="Thread Locked",
            description="🔒 Thread locked and archived",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed)

        try:
            await thread.archive()
        except Exception:
            pass

        try:
            await thread.edit(locked=True)
        except Exception:
            pass


bot.run(os.getenv("TOKEN"))
