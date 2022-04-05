import discord
from discord.ext import commands
from vars import *


class Suggestion:

    def __init__(
            self,
            interaction: discord.Interaction,
            client: commands.Bot,
            msg: discord.Message = None,
    ):
        self.interaction = interaction
        self.msg = msg
        self.client = client

        self.suggestions_channel_id = 958423725462683729

        self.logs_channel_id = 762024716210143234
        self.accepted_suggestions_channel_id = 959481410048118875

        self.upvote_emoji = ":upvote:959491000844288010"
        self.downvote_emoji = ":downvote:959491007035109417"

    def is_suggestion(
            self,
            message: discord.Message
    ) -> bool:
        """
        Returns whether or not the message is a suggestion or not.
        """

        msg = message

        try:
            if msg.embeds is None or msg.embeds[0].title is discord.Embed.Empty:
                return False

            if msg.embeds[0].title.startswith("Suggestion | ") and msg.author == self.client.user:
                return True
            return False
        except IndexError:
            return False

    async def get_author(
            self,
            message: discord.Message
    ) -> discord.User:
        """
        Returns the author of a suggestion.
        """
        msg = message

        try:
            user_id = suggestions_dict[str(msg.id)]["author"]
        except KeyError:
            pass
        else:
            return await self.client.fetch_user(int(user_id))

    async def log(
            self,
            embed: discord.Embed
    ) -> None:
        """
        Sends an embed to the logs channel.
        """
        logs = self.client.get_channel(self.logs_channel_id)
        await logs.send(embed=embed)


    async def deny(
            self,
            suggestion: discord.Message,
            reason: str
    ) -> None:
        """
        Denies a suggestion.
        """

        interaction = self.interaction

        if not self.is_suggestion(suggestion):
            emb = discord.Embed(
                description="That is not a suggestion!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        embed_title = suggestion.embeds[0].title
        embed_desc = suggestion.embeds[0].description
        fields = suggestion.embeds[0].fields
        embed_author = suggestion.embeds[0].author.name
        embed_author_icon = suggestion.embeds[0].author.icon_url

        accept_emb = discord.Embed(
            title="Suggestion | Denied",
            description=embed_desc,
            color=discord.Color.red()
        )
        accept_emb.add_field(
            name=fields[0].name,
            value=fields[0].value,
            inline=False
        )
        accept_emb.add_field(
            name=fields[1].name,
            value=fields[1].value,
            inline=False
        )
        accept_emb.set_author(
            name=f"{embed_author}",
            icon_url=f"{embed_author_icon}"
        )
        accept_emb.set_footer(text=f"Melony Suggestion | Denied by {interaction.user}")
        if reason:
            accept_emb.add_field(name=f"{interaction.user.display_name}'s Response", value=f"{reason}", inline=False)
        if not reason:
            accept_emb.add_field(name=f"{interaction.user.display_name}'s Response", value=f"No response provided.",
                                 inline=False)

        await suggestion.edit(embed=accept_emb)

        accepted_emb = discord.Embed(
            description=f"Successfully denied suggestion. | [Jump to Suggestion]({suggestion.jump_url})",
            color=discord.Color.green()
        )
        accepted_emb.set_footer(text="Melony Suggestion")

        await interaction.response.send_message(embed=accepted_emb, ephemeral=True)

        """
        Log the suggestion.
        """

        log_emb = discord.Embed(
            description=f"Suggestion **denied** by {interaction.user.mention} "
                        f"| [Jump to Suggestion]({suggestion.jump_url})",
            color=discord.Color.green()
        )

        log_emb.set_author(
            name=interaction.user.display_name,
            icon_url=str(interaction.user.avatar)
        )
        log_emb.set_footer(
            text=f"Author: {interaction.user.id} | Message ID: {suggestion.id}"
        )

        await self.log(embed=log_emb)

        """
        Message the user about their suggestion once it's denied.
        """

        emb = discord.Embed(
            description=f"Your suggestion was **denied**. | [Jump to Your Suggestion]({suggestion.jump_url})",
            color=discord.Color.red()
        )

        user = await self.get_author(suggestion)
        if user:
            await user.send(embed=emb)


    async def accept(
            self,
            suggestion: discord.Message,
            reason: str
    ) -> None:
        """
        Accepts a suggestion.
        """
        interaction = self.interaction

        if not self.is_suggestion(suggestion):
            emb = discord.Embed(
                description="That is not a suggestion!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        embed_title = suggestion.embeds[0].title
        embed_desc = suggestion.embeds[0].description
        fields = suggestion.embeds[0].fields
        embed_author = suggestion.embeds[0].author.name
        embed_author_icon = suggestion.embeds[0].author.icon_url

        accept_emb = discord.Embed(
            title="Suggestion | Accepted",
            description=embed_desc,
            color=discord.Color.green()
        )
        accept_emb.add_field(
            name=fields[0].name,
            value=fields[0].value,
            inline=False
        )
        accept_emb.add_field(
            name=fields[1].name,
            value=fields[1].value,
            inline=False
        )
        accept_emb.set_author(
            name=f"{embed_author}",
            icon_url=f"{embed_author_icon}"
        )
        accept_emb.set_footer(text=f"Melony Suggestion | Accepted by {interaction.user}")
        if reason:
            accept_emb.add_field(name=f"{interaction.user.display_name}'s Response", value=f"{reason}", inline=False)
        if not reason:
            accept_emb.add_field(name=f"{interaction.user.display_name}'s Response", value=f"No response provided.",
                                 inline=False)

        await suggestion.edit(embed=accept_emb)

        accepted_emb = discord.Embed(
            description=f"Successfully accepted suggestion. | [Jump to Suggestion]({suggestion.jump_url})",
            color=discord.Color.green()
        )
        accepted_emb.set_footer(text="Melony Suggestion")

        await interaction.response.send_message(embed=accepted_emb, ephemeral=True)

        """
        Log the suggestion.
        """

        log_emb = discord.Embed(
            description=f"Suggestion **accepted** by {interaction.user.mention} | [Jump to Suggestion]({suggestion.jump_url})",
            color=discord.Color.green()
        )

        log_emb.set_author(
            name=interaction.user.display_name,
            icon_url=str(interaction.user.avatar)

        )

        log_emb.set_footer(
            text=f"Author: {interaction.user.id} | Message ID: {suggestion.id}"
        )

        await self.log(embed=log_emb)

        """
        Message the user about their suggestion once it's accepted.
        """

        emb = discord.Embed(
            description=f"Your suggestion was **accepted**. | [Jump to Your Suggestion]({suggestion.jump_url})",
            color=discord.Color.green()
        )

        user = await self.get_author(suggestion)
        if user:
            await user.send(embed=emb)

        """
        Send the suggestion to the accepted suggestions channel.
        """

        accepted_ch = self.client.get_channel(self.accepted_suggestions_channel_id)
        await accepted_ch.send(embed=accept_emb)


    async def reply(
            self,
            suggestion: discord.Message,
            reason: str
    ) -> None:
        """
        Replies to a suggestion.
        """
        interaction = self.interaction

        if not self.is_suggestion(suggestion):
            emb = discord.Embed(
                description="That is not a suggestion!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        embed = suggestion.embeds
        embed_title = embed[0].title
        embed_desc = embed[0].description
        embed_color = embed[0].colour
        fields = embed[0].fields
        embed_footer = embed[0].footer
        embed_author = embed[0].author.name
        embed_author_icon = embed[0].author.icon_url

        reply_emb = discord.Embed(
            title=embed_title,
            description=embed_desc,
            color=embed_color
        )
        reply_emb.add_field(
            name=fields[0].name,
            value=fields[0].value,
            inline=False
        )
        reply_emb.add_field(
            name=fields[1].name,
            value=fields[1].value,
            inline=False
        )
        reply_emb.set_author(
            name=f"{embed_author}",
            icon_url=f"{embed_author_icon}"
        )
        reply_emb.set_footer(text=embed_footer.text)

        reply_emb.add_field(
            name=f"{interaction.user.display_name}'s Response",
            value=f"{reason}", inline=False
        )

        await suggestion.edit(embed=reply_emb)

        accepted_emb = discord.Embed(
            description=f"Successfully replied to suggestion. | [Jump to Suggestion]({suggestion.jump_url})",
            color=discord.Color.green()
        )
        accepted_emb.set_footer(text="Melony Suggestion")

        await interaction.response.send_message(embed=accepted_emb, ephemeral=True)

        """
        Log the suggestion.
        """

        log_emb = discord.Embed(
            description=f"Suggestion **replied to** by {interaction.user.mention} | [Jump to Suggestion]({suggestion.jump_url})",
            color=discord.Color.green())
        log_emb.set_author(name=interaction.user.display_name, icon_url=str(interaction.user.avatar))
        log_emb.set_footer(text=f"Author: {interaction.user.id} | Message ID: {suggestion.id}")

        await self.log(embed=log_emb)

        """
        Message the user about their suggestion once it's replied to.
        """

        emb = discord.Embed(
            description=f"Your suggestion was **replied to**. | [Jump to Your Suggestion]({suggestion.jump_url})",
            color=discord.Color.gold()
        )

        user = await self.get_author(suggestion)
        if user:
            await user.send(embed=emb)

    async def create_suggestion(
            self,
            name: str,
            functionality: str,
            _type: str
    ) -> None:
        """
        Creates a suggestion.
        """
        interaction = self.interaction

        if len(name) > 75:
            emb = discord.Embed(
                description="That name is too long! Please trim it down to something under **75** characters.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        elif len(name) <= 2:
            too_short_emb = discord.Embed(
                description=f"That name is too short! Make an actual name.",
                color=discord.Color.red())
            await interaction.response.send_message(embed=too_short_emb, ephemeral=True)
            return

        if len(functionality) > 450:
            emb = discord.Embed(
                description="That functionality is too long! Please trim it down to something under **350** characters.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        elif len(functionality) <= 10:
            too_short_emb = discord.Embed(
                description=f"That functionality is too short! Please, describe the functinality of your {_type} well.",
                color=discord.Color.red())
            await interaction.response.send_message(embed=too_short_emb, ephemeral=True)
            return

        suggestions_channel = self.client.get_channel(self.suggestions_channel_id)

        suggestion_embed = discord.Embed(
            title=f"Suggestion | Pending",
            description=f"**Type:** `{_type}`",
            color=discord.Color.gold()
        )

        suggestion_embed.add_field(
            name="Name",
            value=name,
            inline=False
        )
        suggestion_embed.add_field(
            name="Functionality",
            value=functionality,
            inline=False
        )

        suggestion_embed.set_author(
            name=interaction.user.display_name,
            icon_url=str(interaction.user.avatar)
        )

        suggestion_embed.set_footer(
            text=f"Melony Suggestion | Pending"
        )

        msg = await suggestions_channel.send(embed=suggestion_embed)

        emb = discord.Embed(
            description=f":white_check_mark: Successfully sent your suggestion into <#{suggestions_channel.id}>."
                        f" | [Jump to Suggestion]({msg.jump_url})",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)

        log_emb = discord.Embed(
            description=f"Suggestion **created** by {interaction.user.mention} | [Jump to Suggestion]({msg.jump_url})",
            color=discord.Color.green())
        log_emb.set_author(name=interaction.user.display_name, icon_url=str(interaction.user.avatar))
        log_emb.set_footer(text=f"Author: {interaction.user.id} | Suggestion ID: {msg.id}")

        await self.log(embed=log_emb)

        suggestions_dict[str(msg.id)] = {
            "author": interaction.user.id
        }
