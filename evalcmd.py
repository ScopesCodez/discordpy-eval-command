import discord
from discord.ext import commands
from traceback import format_exception
import io
import textwrap
import contextlib
from discord.ext.buttons import Paginator
import os

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


class EvalCMD(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eval", aliases=["exec"])
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        code = clean_code(code)

        local_variables = {
            "discord": discord,
            "commands": commands,
            "client": self.bot,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "self": self,
            "os": os
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = str(stdout.getvalue())
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))

        if len(result) > 0:
            pager = Pag(
                timeout=100,
                entries=[result[i: i + 2000]
                         for i in range(0, len(result), 2000)],
                length=1,
                prefix="```\n",
                suffix="```"
            )

            await pager.start(ctx)


def setup(bot):
    bot.add_cog(EvalCMD(bot))
