# modules.utils.commons

from llama_index.core.llms import MessageRole as Role
from disnake.ext import commands
import subprocess
import re

class HistoryChatMessage:
    def __init__(self, content, role, user_name=None, additional_kwargs=None):
        self.content = content
        self.role = role
        self.user_name = user_name
        self.additional_kwargs = additional_kwargs if additional_kwargs else {}

async def fetch_reply_chain(message, max_tokens=4096):
    context = []
    tokens_used = 0
    current_prompt_tokens = len(message.content) // 4
    max_tokens -= current_prompt_tokens
    while message.reference is not None and tokens_used < max_tokens:
        try:
            message = await message.channel.fetch_message(message.reference.message_id)
            role = Role.ASSISTANT if message.author.bot else Role.USER
            user_name = message.author.name if not message.author.bot else None
            message_content = f"{message.content}\n"
            message_tokens = len(message_content) // 4
            if tokens_used + message_tokens <= max_tokens:
                context.append(HistoryChatMessage(message_content, role, user_name))
                tokens_used += message_tokens
            else:
                break
        except Exception as e:
            print(f"Error fetching reply chain message: {e}")
            break
    return context[::-1]

async def send_message(message, content, should_reply):
    try:
        if should_reply:
            return await message.reply(content)
        else:
            return await message.channel.send(content)
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def split_message(response):
    max_length = 2000
    markdown_chars = ['*', '_', '~', '|']
    parts = []
    code_block_type = None
    while len(response) > max_length:
        split_index = response.rfind('\n', 0, max_length)
        split_index = max_length if split_index == -1 else split_index
        part = response[:split_index]
        code_block_start = part.rfind('```')
        code_block_end = part.rfind('```', code_block_start + 3)
        if code_block_start != -1 and (code_block_end == -1 or code_block_end < code_block_start):
            code_block_type = part[code_block_start + 3:].split('\n', 1)[0]
            part += '```'
            response = '```' + (code_block_type + '\n' if code_block_type else '') + response[split_index:].lstrip()
        else:
            response = response[split_index:].lstrip()
        for char in markdown_chars:
            if part.count(char) % 2 != 0 and not part.endswith('```'):
                part += char
                response = char + response
        parts.append(part)
    parts.append(response)
    return parts

async def send_long_message(message, response, should_reply=True):
    chunks = re.split(r'(```.*?```)', response, flags=re.DOTALL)
    result = ''
    for chunk in chunks:
        if chunk.startswith('```'):
            result += chunk
        else:
            chunk = re.sub(r'\((http[s]?://\S+)\)', r'(<\1>)', chunk)
            chunk = re.sub(r'(?<![\(<`])http[s]?://\S+(?![>\).,`])', r'<\g<0>>', chunk)
            result += chunk
    response = result
    messages = []
    parts = split_message(response)
    for part in parts:
        last_message = await send_message(message, part, should_reply)
        if last_message is None:
            break
        messages.append(last_message)
        message = last_message
    return messages

def get_git_version():
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()[:7]
        return f"v2.3 {branch} {commit}"
    except subprocess.CalledProcessError:
        return "unknown-version"
bot_version = get_git_version()

def is_admin():
    async def predicate(ctx):
        author = ctx.user
        is_admin = author.guild_permissions.administrator
        print(f"Checking admin status for {author} (ID: {author.id}): {is_admin}")
        return is_admin
    return commands.check(predicate)

def is_admin_or_user(user_id=126123710435295232):
    async def predicate(ctx):
        is_admin = ctx.author.guild_permissions.administrator
        is_specific_user = ctx.author.id == user_id
        return is_admin or is_specific_user
    return commands.check(predicate)

def is_admin_or_rank(rank_id=1198482895342411846):
    async def predicate(ctx):
        is_admin = ctx.author.guild_permissions.administrator
        has_rank = any(role.id == rank_id for role in ctx.author.roles)
        return is_admin or has_rank
    return commands.check(predicate)
