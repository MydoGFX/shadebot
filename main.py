import traceback
import suggestion
import discord
from discord.ext import commands
from re import search
import random

client = commands.Bot(
    intents=discord.Intents.all()
)

color = 0x286769

guild_id = 945070505252229160


@client.event
async def on_ready():
    print("Bot is online.")


@client.event
async def on_application_command_error(
        ctx: discord.ApplicationContext,
        error
):
    if isinstance(error, commands.MissingPermissions):
        emb = discord.Embed(
            description="You do not have permission to execute this command!",
            color=color
        )
        await ctx.respond(embed=emb, ephemeral=True)

    elif isinstance(error, commands.CommandOnCooldown):
        emb = discord.Embed(
            description=f"You're on cooldown for **{error.retry_after:.2f}s**.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=emb, ephemeral=True)

    traceback.print_exception(type(error), error, error.__traceback__)


@client.slash_command(
    description="Suggest a plugin, feature, patch and more to Shadecraft.",
    guild_ids=[guild_id]
)
@commands.cooldown(
    1, 45, commands.BucketType.user
)
async def suggest(
        ctx: discord.ApplicationContext,

        _type: discord.Option(
            str,
            "Options",
            autocomplete=discord.utils.basic_autocomplete(
                ["Plugin", "Feature", "Patch", "Bot Suggestion", "Other"]
            ),
            name="type",
        )
):
    if _type not in ["Plugin", "Feature", "Patch", "Bot Suggestion", "Other"]:
        emb = discord.Embed(
            description="You suggestion type must be a **Plugin**, **Feature**, **Patch**, **Bot Suggestion**, or **Other**.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=emb, ephemeral=True)
        return

    await ctx.response.send_modal(modal=SuggestionModal(_type))


class SuggestionModal(discord.ui.Modal):
    def __init__(self, _type: str) -> None:
        self.type = _type

        super().__init__("Create a Suggestion")

        self.add_item(
            discord.ui.InputText(
                label="Name",
                placeholder="The name of your suggestion...",
                style=discord.InputTextStyle.short,
                max_length=75,
                min_length=2
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="Functionality",
                placeholder="The functionality of your suggestion...",
                style=discord.InputTextStyle.short,
                max_length=450,
                min_length=10,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        name = self.children[0].value
        functionality = self.children[1].value
        _type = self.type

        sugg = suggestion.Suggestion(
            interaction=interaction,
            client=client
        )
        await sugg.create_suggestion(
            name=name,
            functionality=functionality,
            _type=_type
        )

# Accept Command
@client.slash_command(
    description="Accept a suggestion.",
    guild_ids=[guild_id]
)
@commands.has_permissions(ban_members=True)
async def accept(
        ctx: discord.ApplicationContext,

        message_id: discord.Option(
            str,
            description="The message ID of the suggestion you're accepting."
        ), *,

        reason: discord.Option(
            str,
            description="The reason you're accepting said suggestion.",
            required=False
        ) = None
):
    suggestions_channel = client.get_channel(930576044698779658)

    try:
        _suggestion = await suggestions_channel.fetch_message(int(message_id))
    except discord.DiscordException and ValueError:
        error_suggestion_emb = discord.Embed(description="I can't find that suggestion!", color=discord.Color.red())
        await ctx.respond(embed=error_suggestion_emb, ephemeral=True)
        return

    sugg = suggestion.Suggestion(
        interaction=ctx.interaction,
        client=client
    )
    await sugg.accept(
        suggestion=_suggestion,
        reason=reason
    )


# Accept Command
@client.slash_command(
    description="Denies a suggestion.",
    guild_ids=[guild_id]
)
@commands.has_permissions(ban_members=True)
async def deny(
        ctx: discord.ApplicationContext,

        message_id: discord.Option(
            str,
            description="The message ID of the suggestion you're denying."
        ), *,

        reason: discord.Option(
            str,
            description="The reason you're denying said suggestion.",
            required=False
        ) = None
):
    suggestions_channel = client.get_channel(930576044698779658)

    try:
        _suggestion = await suggestions_channel.fetch_message(int(message_id))
    except discord.DiscordException and ValueError:
        error_suggestion_emb = discord.Embed(description="I can't find that suggestion!", color=discord.Color.red())
        await ctx.respond(embed=error_suggestion_emb, ephemeral=True)
        return

    sugg = suggestion.Suggestion(
        interaction=ctx.interaction,
        client=client
    )
    await sugg.deny(
        suggestion=_suggestion,
        reason=reason
    )


@client.slash_command(
    description="Reply to a suggestion without changing the status.",
    guild_ids=[guild_id]
)
@commands.has_permissions(ban_members=True)
async def reply(
        ctx: discord.ApplicationContext,

        message_id: discord.Option(
            str,
            description="The message ID of the suggestion you're replying to."
        ),

        _reply: discord.Option(
            str,
            name="reply",
            description="The text your reply will be.",
            required=True
        )
):
    suggestions_channel = client.get_channel(930576044698779658)

    try:
        _suggestion = await suggestions_channel.fetch_message(int(message_id))
    except discord.DiscordException and ValueError:
        error_suggestion_emb = discord.Embed(description="I can't find that suggestion!", color=discord.Color.red())
        await ctx.respond(embed=error_suggestion_emb, ephemeral=True)
        return

    sugg = suggestion.Suggestion(
        interaction=ctx.interaction
    )

    await sugg.reply(
        suggestion=_suggestion,
        reason=_reply
    )


@client.slash_command(
    description="Displays useful information about Shadecraft.",
    guild_ids=[guild_id]
)
async def faq(
        ctx: discord.ApplicationContext,

        user: discord.Option(
            discord.Member,
            description="The user who you want to display a FAQ embed to.",
            required=False
        ) = None
):
    emb = discord.Embed(
        title="FAQ",
        description="This is the Shadecraft FAQ picker. Please choose which FAQ embed you want to display below.",
        color=color
    )

    emb.set_footer(text="Shadecraft • FAQ")

    view = discord.ui.View()

    view.add_item(Dropdown(user))

    await ctx.respond(embed=emb, view=view, ephemeral=True)


class Dropdown(discord.ui.Select):
    def __init__(self, user: discord.Member):
        self.user = user

        options = [
            discord.SelectOption(
                label="Release",
                description="Displays information about our release."
            ),
            discord.SelectOption(
                label="Server Info",
                description="Displays information about the server."
            ),
            discord.SelectOption(
                label="Cracked Accounts",
                description="Displays information about us supporting cracked accounts."
            )
        ]

        super().__init__(
            placeholder="Choose which FAQ embed you want...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.disabled:
            emb = discord.Embed(
                description="This dropdown has expired.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        option = self.values[0]
        user = self.user
        channel = client.get_channel(interaction.channel_id)

        if option == "Release":

            announcement_url = "https://discord.com/channels/832361947373895770/887822368871956500/939706663299088415"
            message_url = "https://discord.com/channels/832361947373895770/908480284595486830/939961308357460019"

            emb = discord.Embed(
                title="Shadecraft's Release",
                color=color
            )

            emb.add_field(
                name="Is Shadecraft Released yet?",
                value="No, it isnt. Be sure to look out for updates at #channel",
                inline=False
            )

            emb.set_footer(text=f"Shadecraft • FAQ | Sent by {interaction.user}", icon_url=interaction.user.avatar.url)

            if user:
                await channel.send(
                    f"Hey, {user.mention}",
                    embed=emb
                )
            else:
                await channel.send(embed=emb)

        elif option == "Server Info":
            emb = discord.Embed(
                title="Shadecraft Server Information",
                description=
                """Server IP: mc.shadcraft.ga
Port: 25565
Version: 1.18.2
Website: [shadcraft.ga](https://shadcraft.ga)""",
                color=color

            )
            emb.set_footer(text=f"Shadecraft • FAQ | Sent by {interaction.user}", icon_url=interaction.user.avatar.url)

            if user:
                await channel.send(f"Hey, {user.mention}", embed=emb)
            else:
                await channel.send(embed=emb)

        elif option == "Cracked Accounts":
            emb = discord.Embed(
                title="Cracked Accounts",
                description="You can only play using a Java or bedrock account purchased at [minecraft.net](https://minecraft.net). "
                            "Why? Because we respect [Mojang's EULA](https://account.mojang.com/documents/minecraft_eula) "
                            "and will never try to violate it.",
                color=color
            )
            emb.set_footer(text=f"Shadecraft • FAQ | Sent by {interaction.user}", icon_url=interaction.user.avatar.url)

            if user:
                await interaction.channel.send(f"Hey, {user.mention}", embed=emb)
            else:
                await interaction.channel.send(embed=emb)

        else:
            emb = discord.Embed(
                description="Something went wrong. Please open a ticket.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=emb, ephemeral=True)

        self.disabled = True


@client.slash_command(
    description="Generate a simple embed.",
    guild_ids=[guild_id]
)
@commands.has_permissions(administrator=True)
async def embed(
        ctx: discord.ApplicationContext,

        title: discord.Option(
            str,
            description="The title of the embed.",
            required=False
        ) = None,

        description: discord.Option(
            str,
            description="The description of the embed.",
            required=False
        ) = None,

        footer: discord.Option(
            str,
            description="The footer of the embed.",
            required=False
        ) = None,

        _color: discord.Option(
            str,
            name="color",
            description="The HEX color code of the embed.",
            required=False
        ) = discord.Color.default(),

        thumbnail: discord.Option(
            discord.Attachment,
            description="The thumbnail of the embed.",
            required=False
        ) = None,

        image: discord.Option(
            discord.Attachment,
            description="The image of the embed.",
            required=False
        ) = None,

        content: discord.Option(
            str,
            description="The message you want above the embed.",
            required=False
        ) = None
):
    emb = discord.Embed()

    if title:
        emb.title = title

    if description:
        emb.description = str(description).replace("\\n", "\n")

    if _color:
        # Check if the HEX color is valid.
        match = search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', str(_color))

        if not match:
            invalid_hex = discord.Embed(
                description="That is not a valid HEX color.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=invalid_hex, ephemeral=True)
            return

        emb.colour = int(str(_color).replace("#", "0x"), 16)

    if footer:
        emb.set_footer(text=footer)

    if thumbnail:
        emb.set_thumbnail(url=thumbnail.url)

    if image:
        emb.set_image(url=image.url)

    try:
        if content:
            await ctx.channel.send(content=content, embed=emb)
        else:
            await ctx.channel.send(embed=emb)
    except discord.DiscordException:
        invalid_emb = discord.Embed(
            description="That embed is not a valid Discord embed. Maybe you typed some parameters wrong?",
            color=discord.Color.red()
        )
        await ctx.respond(embed=invalid_emb, ephemeral=True)
        return

    success_emb = discord.Embed(
        description="Successfully created your embed.",
        color=discord.Color.green()
    )
    await ctx.respond(embed=success_emb, ephemeral=True)


# joke Command
@client.slash_command(
    guild_ids=[guild_id],
    name="joke",
    description="Tells a joke!"
)
async def joke(
        ctx: discord.ApplicationContext,
):
    responses = [
        "What’s the best thing about Switzerland? I don’t know, but the flag is a big plus.",
        "I invented a new word! Plagiarism!",
        "Did you hear about the mathematician who’s afraid of negative numbers? He’ll stop at nothing to avoid them.",
        "Yesterday I saw a guy spill all his Scrabble letters on the road. I asked him, “What’s the word on the street?”",
        "Hear about the new restaurant called Karma? There’s no menu: You get what you deserve.",
        "Did you hear about the first restaurant to open on the moon? It had great food, but no atmosphere.",
        "What did one ocean say to the other ocean? Nothing, it just waved.",
        "Did you hear about the fire at the circus? It was in tents!",
        "Why do ducks have feathers? To cover their butt quacks!",
        "What’s the difference between a hippo and a zippo? One is really heavy and the other’s a little lighter.",
        "What does a nosey pepper do? It gets jalapeño business. ",
        "Why should you never trust stairs? They’re always up to something.",
        "When does a joke become a ‘dad’ joke? When it becomes apparent.",
        "Why did the bullet end up losing his job? He got fired.",
        "What kind of shorts do clouds wear? Thunderpants",
        "How do you measure a snake? In inches—they don’t have feet.",
        "Where does a waitress with only one leg work? IHOP.",
        "What does a house wear? Address!",
        "Why is Peter Pan always flying? Because he Neverlands. (I love this joke because it never grows old.)",
        "You heard the rumor going around about butter? Never mind, I shouldn’t spread it.",
        "The first rule of the Alzheimer’s club is… Wait, where are we again?",
        "What do you get from a pampered cow? Spoiled milk.",
        "How does NASA organize a party? They planet.",
        "You know, it was so cold in D.C. the other day, I saw a politician with his hands in his *own* pockets.",
        "What gets wetter the more it dries? A towel.",
        "discord kittens...",
        "I don’t have a carbon footprint. I just drive everywhere.",
        "The most corrupt CEOs are those of the pretzel companies. They’re always so twisted.",
        "When we were kids, we used to be afraid of the dark. But when we grew up, the electricity bill made us afraid of the light!An apple a day keeps the doctor away… Or at least it does if you throw it hard enough.",
        "I visited my friend at his new house. He told me to make myself at home. So I threw him out. I hate having visitors.",
        "I was playing chess with my friend and he said, “Let’s make this interesting.” So we stopped playing chess.",
        "The other day, my wife asked me to pass her lipstick, but I accidentally passed her a glue stick. She still isn’t talking to me.",
        "Patient: Oh doctor, I’m just so nervous. This is my first operation. Doctor: Don’t worry. Mine too.",
        "Never break someone’s heart. They only have one. Break their bones instead. They have 206 of them.",
        "My husband is mad that I have no sense of direction. So I packed up my stuff and right.",
        "I childproofed my house Somehow they still got in!",
        "The guy who stole my diary just died. My thoughts are with his family.",
        "What’s worse than biting into an apple and discovering a worm? Biting into an apple and discovering half a worm.",
        "As I get older, I remember all the people I lost along the way. Maybe a career as a tour guide was not the right choice.",
        "My wife told me she’ll slam my head into the keyboard if I don’t get off the computer. I’m not too worried — I think she’s jokindkdkslalkdlkfjslfjslksdlkfjuahehwhgwdklaljdfrtsdfygsdyuifgiedusjfsdiuyf",
        "You’re not completely useless. You can always serve as a bad example.",
        "“Welcome back to Plastic Surgery Anonymous. Nice to see so many new faces here today!”",
        "My wife left a note on the fridge that said, “This isn’t working.” I’m not sure what she’s talking about. I opened the fridge door and it’s working fine!",
        "My boss told me to have a good day. So I went home.",
        "Imagine when you walked into a bar and there was a lengthy line of individuals ready to take a swing at you. That’s the punch line.",
        "Wife: “I want another baby.” Husband: “That’s a relief, I also really don’t like this one.”",
        "“What’s your name, son?” The principal asked his student. The kid replied, “D-d-d-dav-dav-david, sir.” “Do you have a stutter?” the principal asked. The student answered, “No sir, my dad has a stutter but the guy who registered my name was a real jerk.”",
        "Why are friends a lot like snow? If you pee on them, they disappear.",
        "I threw a boomerang a few years ago. I now live in constant fear.",
        "A blind woman tells her boyfriend that she’s seeing someone. It’s either terrible news or great news.",
        "My boss said to me, “You’re the worst train driver ever. How many have you derailed this year?” I said, “I’m not sure; it’s hard to keep track.”",
        "What do you call a fish without eyes? Fsh.",
        "What do you call an alligator detective? An investi-gator.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "There are two muffins baking in the oven. One muffin says to the other, “Phew, is it getting hot in here or is it just me?” The other muffin says, “AAAAHHH!! A TALKING MUFFIN!”",
        "What lights up a soccer stadium? A soccer match.",
        "Why shouldn’t you write with a broken pencil? Because it’s pointless.",
        "I spilled spot remover on my dog. Now he’s gone.",
        "I could tell that my parents hated me. My bath toys were a toaster and a radio.",
        "Dogs are forever in the pushup position.",
        "A cannibal is a person who walks into a restaurant… and orders a waiter.",
        "I stayed up one night playing poker with Tarot cards. I got a full house and four people died.",
        "Congress is the finest group… money can buy.",
        "I was such an ugly person… when I played in the sandbox, the cat kept covering me up.",
        "I am a man of my word, and that word is “unreliable.”",
        "New York now leads the world’s great cities… in the number of people around whom you shouldn’t make a sudden move.",
        "What did the evil chicken lay? Deviled eggs.",
        "How do you make holy water? You boil the hell out of it.",
        "What sound does a witch’s car make? Broom broom!",
        "What’s the best way to watch a fly-fishing tournament? Live stream.",
        "How do you tell the difference between an alligator and a crocodile? You will see one later and one in a while.",
        "Why did the man name his dogs Rolex and Timex? Because they were watch dogs.",
        "What do you call a dog that can do magic? A Labracabrador.",
        "Why do dogs float in water? Because they are good buoys.",
        "Why do cows wear bells? Because their horns don’t work.",
        "What happens when it rains cats and dogs? You have to be careful not to step in a poodle.",
        "Why is grass so dangerous? Because it’s full of blades.",
        "What do you call a fake noodle? An impasta.",
        "A college education now costs $100,000, but it produces three very proud people—the student, his mama, and his pauper.",
        "What does a mobster buried in cement soon become? A hardened criminal.",
        "My IQ test results came back. They were negative.",
        "What do you get when you cross a polar bear with a seal? A polar bear.",
        "What do you call a bear with no teeth? A gummy bear.",
        "Did you hear about the nurse who was chewed out by the doctor because she was absent without gauze?",
        "My wife asked me to sync her phone, so I threw it into the ocean.",
        "What did one cannibal say to the other while they were eating a clown? Does this taste funny to you?",
        "What do you call someone with no body and no nose? Nobody knows.",
        "Can February March? No, but April May.",
        "What kind of exercise do lazy people do? Diddly-squats.",
        "What do you call a pony with a cough? A little horse!",
        "Why did the M&M go to school? He wanted to be a Smartie.",
        "What did one traffic light say to the other? Stop looking at me, I'm changing!",
        "What do you call bears with no ears? B)",
        "What's a foot long and slippery? A slipper!",
        "Why do French people eat snails? They don't like fast food!",
        "What's red and moves up and down? A tomato in an elevator!",
        "What is sticky and brown? A stick!",
        "What is sticky and white? ;)",
        "How does a rabbi make coffee? Hebrews it!",
        "Rest in peace boiling water. You will be mist!",
        "Want to hear a construction joke? Oh never mind, I'm still working on that one.",
        "Why don't scientists trust atoms? Because they make up everything!",
        "Talk is cheap? Have you ever talked to a lawyer?",
        "Why did the gym close down? It just didn't work out!",
        "Two artists had an art contest. It ended in a draw!",
        "A plateau is the highest form of flattery.",
        "I have a fear of speed bumps. But I am slowly getting over it.",
        "What do you call a boomerang that doesn't come back? A stick!",
        "You know what I saw today? Everything I looked at.",
        "What are a shark's two most favorite words? Man overboard!",
        "If we shouldn't eat at night, why do they put a light in the fridge?",
        "Have you ever tried eating a clock? It's really time-consuming, especially if you go for seconds.",
        "Why are ghosts such bad liars? Because they are easy to see through.",
        "What did the buffalo say when his son left for college? Bison!",
        "Here, I bought you a calendar. Your days are numbered now.",
        "Where do fish sleep? In the riverbed.",
        "What did one plate say to his friend? Tonight, dinner's on me!",
        "Where are average things manufactured? The satisfactory.",
        "I tried to sure the airport for misplacing my luggage. I lost my case.",
        "Why doesn't the sun go to college? Because it has a million degrees!",
        "I was wondering why the frisbee was getting bigger, then it hit me.",
        "I have many jokes about rich kids—sadly none of them work.",
        "What do you call a singing laptop? A Dell!",
        "Why was six afraid of seven? Because seven ate nine.",
        "Why are skeletons so calm? Because nothing gets under their skin.",
        "How do trees get online? They just log on!"
    ]
    emojizz = [
        ":joy_cat:",
        ":rofl:",
        ":joy:",
        ":sweat_smile:",
        ":laughing:",
        ":smile_cat:",
        ":joy_cat:",
        ":disguised_face:",
        ":exploding_head:",
        ":star_struck:",
        ":zany_face:"
    ]

    emb = discord.Embed(
        description=f'**{random.choice(responses)}** {random.choice(emojizz)}',
        color=286769
    )

    await ctx.respond(embed=emb)

# Boop Command
@client.slash_command(
    guild_ids=[guild_id],
    description="boops someone"
)
@commands.cooldown(1,30,commands.BucketType.user)
async def boop(
        ctx: discord.ApplicationContext,

        member: discord.Option(
            discord.Member,
            description="The member you want to booooop."
        )
):

    emb = discord.Embed(
        description=f"{ctx.user.mention}  booped you! <3",
        color=discord.Color.red()
    )
    try:
        await member.send(embed=emb)
    except discord.HTTPException:
        error_emb = discord.Embed(
            description=f"I failed to boop {member.name}. Their DMs are probably off. :(",
            color=discord.Color.red()
        )
        await ctx.respond(embed=error_emb, ephemeral=True)
        return

    emb = discord.Embed(
        description=f"I just booped {member.name}.",
        color=discord.Color.green()
    )
    await ctx.respond(embed=emb, ephemeral=True)
# Bonk Command
@client.slash_command(
    guild_ids=[guild_id],
    description="bonk"
)
@commands.cooldown(1,30,commands.BucketType.user)
async def bonk(
        ctx: discord.ApplicationContext,

        member: discord.Option(
            discord.Member,
            description="The member you want to bonk."
        )
):
    emb = discord.Embed(
        description=f"{ctx.user.mention} just bonked you! L",
        color=discord.Color.red()
    )
    try:
        await member.send(embed=emb)
    except discord.HTTPException:
        error_emb = discord.Embed(
            description=f"I failed to bonk {member.name}. Their DMs are probably off. :(",
            color=discord.Color.red()
        )
        await ctx.respond(embed=error_emb, ephemeral=True)
        return

    emb = discord.Embed(
        description=f"I just bonked {member.name}.",
        color=discord.Color.green()
    )
    await ctx.respond(embed=emb, ephemeral=True)


# gay Command
@client.slash_command(
    guild_ids=[guild_id],
    name="gay",
    description="Shows how gay someone is."
)
async def gay(
        ctx: discord.ApplicationContext,

        user: discord.Option(
            discord.Member,
            description="Choose the user to see how gay they are.",
            required=True
        )
):
    emb = discord.Embed(
        description=f'{user.mention} is {random.randint(-10, 110)}% gay.',
        color=286769
    )
    await ctx.respond(embed=emb)


# 8ball Command
@client.slash_command(
    guild_ids=[guild_id],
    name="8ball",
    description="Gives you a random yes or no response."
)
async def eightball(
        ctx: discord.ApplicationContext,

        question: discord.Option(
            str,
            description="The question you want to ask the bot.",
            required=True
        )
):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful.",
        "Ask Jayren.",
        "Ask the nearest person next to you.",
        "I better not answer that... 😳",
        "yesn't",
        "maybe",
        "im a bot why r u asking me smh my head my head",
        "FOR SPARTAAAA",
        "fs",
        "ofc bestie <3",
        "never.",
        "i'm offended u even tried to ask me that. pfft.",
        "ask Laser idk",
        "ask google",
        "ur mooooom",
        "yes ofccccc",
        "buy any rank and then i'll tell u (jk) (unless)",
        "ask your mom",
        "I honestly have no clue.",
        "me when I yea",
        "my gut instinct says no",
        "my gut instinct says yes",
        "only if you love me <3",
        "ily and I would do anything for you"
    ]

    emb = discord.Embed(
        title=f'{question}',
        description=f'{random.choice(responses)}',
        color=286769
    )
    await ctx.respond(embed=emb)


# pfp Command
@client.slash_command(
    guild_ids=[guild_id],
    name="pfp",
    description="make this your pfp for however long days"
)
async def pfp(
        ctx: discord.ApplicationContext,
):
    sslap = [
        "https://i.pinimg.com/474x/43/d1/1f/43d11f461df5606a9d5219c2ec657de7.jpg",
        "https://i.pinimg.com/originals/f1/85/e4/f185e40cb73dfecd429561013d1376e7.jpg",
        "https://i.pinimg.com/236x/71/9c/d6/719cd642dd0b32be8fe3533442e8a849.jpg",
        "https://i.pinimg.com/736x/45/fe/b6/45feb6d472ac876a905cb860a5394716.jpg",
        "https://emoji.gg/assets/emoji/6510-u-dumb.png",
        "https://i.pinimg.com/236x/29/4d/46/294d46005a915dc1c62d466b26add87b.jpg",
        "https://i.redd.it/nt20w6xo0bd51.jpg",
        "https://i.pinimg.com/736x/91/12/ea/9112eab807a06a3c344e870aa65ad05b.jpg",
        "https://data.whicdn.com/images/326577748/original.jpg",
        "https://emoji.gg/assets/emoji/2788_stupid.png",
        "https://stickers.gg/assets/stickers/9099-mr-twinkies.png",
        "https://i.pinimg.com/236x/c2/62/6b/c2626b83629235bd41c196363229a1c9.jpg",
        "https://i.pinimg.com/236x/c0/5a/6a/c05a6a91ddb30de42859d27c6abd165b.jpg",
        "https://i.pinimg.com/originals/51/8f/b3/518fb3b3536908450b2f5bf2f35ad12a.jpg",
        "https://preview.redd.it/f3qvuqx2u7f71.jpg?width=640&crop=smart&auto=webp&s=5125bae37ac8a1ecb52656f81ae23d7fdf0f914b",
        "https://preview.redd.it/zalskrx2u7f71.jpg?width=485&format=pjpg&auto=webp&s=02840e369dff0216796d23ec8ea85ac0818f182e",
        "https://i.pinimg.com/474x/e0/37/85/e037856df91c6b9eb3347a4ced72dccc.jpg",
        "https://pfps.gg/assets/pfps/1885-corn-flake.png",
        "https://i.pinimg.com/originals/05/6c/ac/056cacfb7eecfe64bbc70cdb472cd5d3.jpg",
        "https://preview.redd.it/918t1z609oh81.jpg?width=640&crop=smart&auto=webp&s=7756e2eba8d53ef877a212bce8a504301f7485a3",
        "https://preview.redd.it/ukyem44jei261.png?auto=webp&s=584b57c95c8d561f26bf1b4290bbcf0f5fde7bb5",
        "https://i.pinimg.com/originals/33/30/b8/3330b81bdf1fc1748c61575e8a56272c.jpg",
        "https://pbs.twimg.com/media/Ef1sdnrXgAMhdXz.jpg",
        "https://i.pinimg.com/736x/82/28/b8/8228b803e31285ec8f745f5f009c93da.jpg",
        "https://i.pinimg.com/550x/80/01/73/800173d0a83b1e3a0873c44fc395dc3a.jpg",
        "https://pm1.narvii.com/7403/180ba973512e6fad8532dd855b0d04c37acff2e7r1-576-472v2_00.jpg",
        "https://i1.sndcdn.com/artworks-zbq2fzqyzIKyJFJT-wXv50g-t500x500.jpg",
        "https://i.pinimg.com/originals/48/78/f0/4878f00d81b0552daf6f489a23fb2920.jpg",
        "https://i.pinimg.com/originals/91/3d/9f/913d9f02a0045a0d53106fd672a4689b.jpg",
        "https://a.wattpad.com/useravatar/DaniDevito0517.256.446097.jpg",
        "https://en.meming.world/images/en/b/bc/Mike_Wazowski-Sulley_Face_Swap.jpg",
        "https://i1.sndcdn.com/avatars-000245805827-8uhxg0-t500x500.jpg",
        "https://cdn.discordapp.com/attachments/936023036849713152/949490965201182850/IMG_2624.jpg",
        "https://i1.sndcdn.com/avatars-E7rx8zyDF13zjb3Y-HYPyPQ-t500x500.jpg"
    ]
    emb = discord.Embed(
        description=f'{ctx.user.mention} has to use this pfp for {random.randint(1, 30)} days.',
        color=286769
    )
    emb.set_image(
        url=f'{random.choice(sslap)}')
    await ctx.respond(embed=emb)
# Bonk Command
@client.slash_command(
    guild_ids=[guild_id],
    description="bonk"
)
@commands.cooldown(1,30,commands.BucketType.user)
async def bonk(
        ctx: discord.ApplicationContext,

        member: discord.Option(
            discord.Member,
            description="The member you want to bonk."
        )
):
    emb = discord.Embed(
        description=f"{ctx.user.mention} just bonked you! L",
        color=286769
    )
    try:
        await member.send(embed=emb)
    except discord.HTTPException:
        error_emb = discord.Embed(
            description=f"I failed to bonk {member.name}. Their DMs are probably off. :(",
            color=discord.Color.red()
        )
        await ctx.respond(embed=error_emb, ephemeral=True)
        return

    emb = discord.Embed(
        description=f"I just bonked {member.name}.",
        color=286769
    )
    await ctx.respond(embed=emb, ephemeral=True)



# Flip a coin Command
@client.slash_command(
    guild_ids=[guild_id],
    name="flipacoin",
    description="Flips a coin for you!"
)
async def flipacoin(
        ctx: discord.ApplicationContext,
):
    responses = [
        "Heads!",
        "Tails!"
    ]
    emb = discord.Embed(
        title=f'{random.choice(responses)}',
        color=286769
    )
    emb.set_image(
        url="https://thumbs.gfycat.com/BabyishShrillKomododragon-max-1mb.gif%22")
    await ctx.respond(embed=emb)


client.run("OTQ1MDcyMTYzOTE5MTE0MjQx.YhK1Cg.x8oaBVRvoPPU_57_84xIHkoh82Q")
