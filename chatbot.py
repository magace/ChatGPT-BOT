import os
import time
import json
import requests
import logging
from openai import OpenAI, RateLimitError
from openai.types.chat.chat_completion import ChatCompletion
from unidecode import unidecode
from tenacity import retry, wait_random_exponential, stop_after_attempt, RetryError
import discord

# ========== Setup Logging ==========
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class ChatDiscordBot(discord.Client):
    def __init__(self, config, client, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.client = client
        self.prefix = config["commant_prefix"]
        self.allowed_channels = config.get("allowed_channel_ids", [])
        self.token_price = float(config["TOKEN_COST"])
        self.model = config["GPT_VERSION"]
        self.pre_message = config["PRE_MESSAGE"]

    async def on_ready(self):
        print(f"✅ Discord bot ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id not in self.allowed_channels:
            return

        if not message.content.startswith(self.prefix):
            return

        user_input = message.content[len(self.prefix):].strip()
        prompt = self.pre_message + user_input

        await message.channel.typing()

        try:
            conversation = [{"role": "user", "content": prompt}]
            response_obj = ask_chat_gpt(self.client, conversation, self.model)
            response = response_obj.choices[0].message.content.strip()
            tokens_used = response_obj.usage.total_tokens
            cost_usd = (tokens_used / 1000) * self.token_price
            # reply = f"🧠 {response}\n\n📊 `{tokens_used} tokens used, ${cost_usd:.5f}`"
            reply = f"{response}"
            await message.reply(reply)
        except Exception as e:
            await message.reply(f"⚠️ Error: {e}")

# ========== Load Config ==========
def load_config():
    try:
        with open("config.json") as f:
            config = json.load(f)
        required_keys = ["OPENAI_API_KEY", "DIRECTORIES", "DISCORD_HOOK", "GPT_VERSION", "PRE_MESSAGE", "TOKEN_COST"]
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required config key: {key}")
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        exit(1)

# ========== Send to Discord ==========
def send_to_discord(webhook_url, content):
    try:
        response = requests.post(webhook_url, json={"content": content})
        if response.status_code != 204:
            raise Exception(f"Discord POST returned {response.status_code}:\n{response.text}")
    except Exception as e:
        logging.warning(f"Discord send failed: {e}")

# ========== Ask GPT with Exponential Retry ==========
@retry(wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6), reraise=True)
def ask_chat_gpt(client: OpenAI, conversation: list, model: str, max_tokens=100) -> ChatCompletion:
    return client.chat.completions.create(
        model=model,
        messages=conversation,
        max_tokens=max_tokens,
    )

# ========== Process Single Question ==========
def process_question(name, directory, config, client):
    question_file = os.path.join(directory, "question.txt")
    answer_file = os.path.join(directory, "answer.txt")

    if not os.path.exists(question_file):
        return

    try:
        with open(question_file, "r") as f:
            user_question = f.read().strip()

        if ' ' in user_question:
            first_word, question_text = user_question.split(' ', 1)
        else:
            first_word = user_question
            question_text = ''

        user_input = config["PRE_MESSAGE"] + first_word + ' ' + question_text
        print(f"📨 {name}: {user_input}")

        send_to_discord(config["DISCORD_HOOK"], f"Question from {name}: {user_input}")

        start_time = time.time()
        conversation = [{"role": "user", "content": user_input}]
        response_obj = ask_chat_gpt(client, conversation, config["GPT_VERSION"])
        end_time = time.time()

        response = response_obj.choices[0].message.content.strip()
        tokens_used = response_obj.usage.total_tokens
        cost_usd = (tokens_used / 1000) * float(config["TOKEN_COST"])

        with open(answer_file, "w") as f:
            f.write(unidecode(response).replace('\n', ' '))

        send_to_discord(
            config["DISCORD_HOOK"],
            f"✅ Question from {name} ({first_word}): {question_text}\n🧠 Answer: {response}"
        )
        print(f"✅ Answered. Tokens: {tokens_used}, Cost: ${cost_usd:.5f}, Time: {end_time - start_time:.2f}s")
        os.remove(question_file)
    except RateLimitError as e:
        logging.warning(f"Rate limit hit: {e}")
    except RetryError as e:
        logging.error(f"Retry failed: {e.last_attempt.exception()}")
    except Exception as e:
        logging.error(f"Unexpected error for {name}: {e}")

# ========== Main Loop ==========
def main():
    config = load_config()
    client = OpenAI(api_key=config["OPENAI_API_KEY"])
    print("📡 Chatbot started. Monitoring for questions...")
    while True:
        for name, directory in config["DIRECTORIES"].items():
            process_question(name, directory, config, client)
        time.sleep(1)
if __name__ == "__main__":
    config = load_config()
    client = OpenAI(api_key=config["OPENAI_API_KEY"])
    # Start local file watcher loop
    import threading
    threading.Thread(target=main, daemon=True).start()
    # Setup Discord intents
    intents = discord.Intents.default()
    intents.message_content = True  # REQUIRED for reading user messages
    # Start Discord bot
    discord_bot = ChatDiscordBot(config, client, intents=intents)
    discord_bot.run(config["bot_token"])

