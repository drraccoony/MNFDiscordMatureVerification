import random, os, datetime
import discord
from discord.ext import commands
from discord import ui, ButtonStyle, File
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration Variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
RULES_CHANNEL_ID = 123456789012345678  # Replace with the ID of the channel where rules are posted
ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL_ID'))
MATURE_ROLE_ID = int(os.getenv('MATURE_ROLE_ID'))
PREFIX = '!'  # Command prefix, e.g., '!verify'
SECRET_PHRASES = [
    "skol",
    "furrymigration",
    "thats a lot of lakes",
    "silver wolf",
    "emerald serpent",
    "lorem ipsum",
    "foobar beans",
    "owo",
    "wut dis"
]

# Store secret phrases temporarily
# TODO: Put this in a flatfile DB or something so its not lost on reboots
pending_verifications = {}

# Intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Event: Bot Ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Command to start the verification process
@bot.command()
async def verify(ctx):
    # Select a random secret phrase
    secret_phrase = random.choice(SECRET_PHRASES)
    pending_verifications[ctx.author.id] = secret_phrase

    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] User {ctx.author.name} ({ctx.author.id}) has started verification process with secret phrase {secret_phrase}.')

    # Leading and trailing text
    leading_text = (
        "Hello! 👋\n\n"
        "We have a mature channel that is still prone to the rules of the server, but a space without minors. "
        "The purpose of this space is to clear any concern about talking about things like alcohol or other topics and being of potential influence to minors. "
        "Pay close attention to these rules as one contains a secret phrase you'll need to provide.\n\n"
        "Here are the rules you need to follow: "
    )

    trailing_text = (
        "\n"
        "✅  Examples of acceptable ID: School ID, Non-driver's license, driver's license, passport, college ID, etc.\n"
        "🚫  Examples of invalid ID: Utility bill, Goofy Goober Membership Card, Membership Cards, Birth Certificate."
    )

    # List of rules with a placeholder for the secret phrase
    rules = [
        "1. NSFW content is still not allowed in this channel, as are all other rules still enforced.",
        "2. Falsifying your age to gain access is grounds for suspension from the Discord server, and possibly MNFurs events (including, but not limited to Furry Migration and Midwinter Frolic).",
        "3. Follow Discord's Terms of Service and Community Guidelines.",
        f"4. To proceed, you'll need the phrase '{secret_phrase}'. This is important.",
        "5. MNFurs Staff and Board may revoke mature role at any time, with or without reason."
    ]

    # Combine the leading text, rules, and trailing text into one message
    embed = discord.Embed(
        title="Server Rules for Mature Role Verification",
        description=f"{leading_text}\n\n" + "\n".join(rules) + f"{trailing_text}",
    )

    embed.set_footer(text="Please read all the rules carefully and follow the instructions.")

    # Send the rules embed to the user via DM
    await ctx.author.send(embed=embed)

    # Inform the user of the next step
    await ctx.author.send(
        "After reading the rules, please send me the secret phrase hidden within the rules, "
        "along with a photo of your ID for verification."
    )

# View for approve/deny buttons
class ApprovalView(ui.View):
    def __init__(self, user, original_message):
        super().__init__(timeout=None)
        self.user = user
        self.original_message = original_message

    @ui.button(label="Approve", style=ButtonStyle.success, emoji="✅")
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        # Fetch the member object from the guild
        guild = interaction.guild
        member = guild.get_member(self.user.id)

        if not member:
            await interaction.response.send_message("User is not in the server or could not be found.", ephemeral=True)
            return

        # Get the mature role
        role = guild.get_role(MATURE_ROLE_ID)

        # Add the role to the member
        await member.add_roles(role)

        # Notify the user
        await self.user.send("✅ Your verification request has been approved! You now have access to mature content.")
        await interaction.response.send_message(f"{member.mention} has been approved and given the mature role.", ephemeral=True)

        # Edit the original message to indicate approval with the admin's name
        await self.original_message.edit(content=f"✅ **Approved by {interaction.user.mention}**", view=None)

    @ui.button(label="Deny", style=ButtonStyle.danger, emoji="⛔")
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        # Fetch the member object from the guild
        guild = interaction.guild
        member = guild.get_member(self.user.id)

        if not member:
            await interaction.response.send_message("User is not in the server or could not be found.", ephemeral=True)
            return

        # Notify the user
        await self.user.send("❌ Your verification request has been denied. Please try again in a few weeks.")
        await interaction.response.send_message(f"{member.mention}'s verification request has been denied.", ephemeral=True)

        # Edit the original message to indicate denial with the admin's name
        await self.original_message.edit(content=f"❌ **Denied by {interaction.user.mention}**", view=None)

# Listen for direct messages with the verification data
@bot.event
async def on_message(message):
    if message.guild is None and not message.author.bot:
        user_id = message.author.id
        secret_phrase = pending_verifications.get(user_id)

        # Check if the user has initiated the verification process
        if not secret_phrase:
            await message.author.send("You haven't started the verification process. Please use the `!verify` command in the server.")
            return

        # Check if the message has an attachment and the secret phrase
        if message.attachments and secret_phrase in message.content.lower():
            attachment = message.attachments[0]

            # Validate that the attachment is an image
            if not attachment.content_type or not attachment.content_type.startswith("image/"):
                await message.author.send("Please upload a valid image file (PNG, JPEG, etc.). Other file types are not allowed.")
                return

            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

            # Download the attached image
            img_data = await attachment.read()
            img_file = File(BytesIO(img_data), filename=attachment.filename)

            # Clean the message content by stripping leading and trailing whitespace
            cleaned_content = message.content.strip()

            # Create an embed for the admin channel
            embed = discord.Embed(
                title="Verification Request",
                description=f"**User:** {message.author.mention}\n"
                            f"**Secret Phrase:** {cleaned_content}",
                color=discord.Color.orange()
            )

            # Send data to the admin channel with buttons and store the original message
            original_message = await admin_channel.send(
                content="A new verification request has been received:",
                embed=embed,
                file=img_file
            )

            # Create the ApprovalView with the original message reference
            view = ApprovalView(message.author, original_message)
            await original_message.edit(view=view)

            print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] User {message.author.name} successfully submitted verification for approval.')

            await message.author.send(
                "Thank you for submitting your verification request! Please wait while an admin reviews your request."
            )

            # Remove the user from pending verifications
            del pending_verifications[user_id]

        else:
            await message.author.send(
                "Please ensure you send both the secret phrase and a photo ID attachment."
            )

    await bot.process_commands(message)

# Command for admins to accept verification
@bot.command()
@commands.has_permissions(administrator=True)
async def accept(ctx, user: discord.Member):
    role = ctx.guild.get_role(MATURE_ROLE_ID)
    await user.add_roles(role)
    await user.send("Congratulations! Your verification request has been approved, and you now have access to the mature channels.")
    await ctx.send(f"{user.mention} has been granted the mature role.")

# Command for admins to deny verification
@bot.command()
@commands.has_permissions(administrator=True)
async def deny(ctx, user: discord.Member):
    await user.send("Sorry, your verification request has been denied. Please try again in a few weeks.")
    await ctx.send(f"{user.mention}'s verification request has been denied.")

# Error handling for missing permissions
@accept.error
@deny.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

# Run the bot
bot.run(TOKEN)
