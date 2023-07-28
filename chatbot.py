import os
import openai
import time
from rich import print
from unidecode import unidecode
import requests
import json


def load_config():
    with open("config.json") as json_file:
        config = json.load(json_file)
    return config

def send_to_discord(webhook_url, content):
    data = {"content": content}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        raise Exception(
            f"POST to discord returned {response.status_code}, the response is:\n{response.text}"
        )

def ask_chat_gpt(conversation, model="gpt-3.5-turbo", max_tokens=100):
    response = openai.ChatCompletion.create(
        model=model, messages=conversation, max_tokens=max_tokens
    )
    return response

def main():
    config = load_config()
    api_key = config["OPENAI_API_KEY"]
    directories = config["DIRECTORIES"]
    openai.api_key = api_key
    discord_hook = config["DISCORD_HOOK"]
    pre_message = config["PRE_MESSAGE"]
    token_price = config["TOKEN_COST"]
    while True:
        for name, directory in directories.items():
            question_file_path = os.path.join(directory, "question.txt")
            answer_file_path = os.path.join(directory, "answer.txt")
            if os.path.exists(question_file_path):
                with open(question_file_path, "r") as question_file:
                    user_input = question_file.readline().strip()
                    user_input = pre_message + user_input
                    print(f"[cyan]Question received from {name}: {user_input}[/cyan]")
                    send_to_discord(
                        discord_hook, f"Question received from {name}: {user_input}"
                    )
                conversation = [{"role": "user", "content": user_input}]
                response = ask_chat_gpt(conversation)
                print(
                    f"[green]Answer from ChatGPT: {response['choices'][0]['message']['content']}[/green]"
                )
                send_to_discord(
                    discord_hook,
                    f"[green]Answer from ChatGPT: {response['choices'][0]['message']['content']}[/green]",
                )
                response_obj = ask_chat_gpt(conversation)
                response = response_obj["choices"][0]["message"]["content"].strip()
                response = unidecode(response)
                tokens_used = response_obj["usage"]["total_tokens"]
                cost_usd = tokens_used * token_price
                print(f"Tokens used: {tokens_used}")
                print(f"Estimated cost (USD): {cost_usd}")
                with open(answer_file_path, "w") as answer_file:
                    response_no_newlines = response.replace("\n", " ")
                    answer_file.write(response_no_newlines)
                os.remove(question_file_path)
        time.sleep(1)

if __name__ == "__main__":
    main()
