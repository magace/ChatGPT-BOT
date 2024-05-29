import os
import openai
import time
from rich import print
from unidecode import unidecode
import requests
import json
import tenacity
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
@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(3))
def ask_chat_gpt(conversation, model, max_tokens=100):
    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation,
        max_tokens=max_tokens,
    )
    return response
def main():
    config = load_config()
    api_key = config["OPENAI_API_KEY"]
    directories = config["DIRECTORIES"]
    openai.api_key = api_key
    discord_hook = config["DISCORD_HOOK"]
    gpt_version = config["GPT_VERSION"]
    pre_message = config["PRE_MESSAGE"]
    token_price = float(config["TOKEN_COST"])
    while True:
        for name, directory in directories.items():
            question_file_path = os.path.join(directory, "question.txt")
            answer_file_path = os.path.join(directory, "answer.txt")
            if os.path.exists(question_file_path):
                with open(question_file_path, "r") as question_file:
                    user_question = question_file.read().strip()
                    user_input = pre_message + user_question
                    print(f"[cyan]Question received from {name}: {user_input}[/cyan]")
                    send_to_discord(
                        discord_hook, f"Question received from {name}: {user_input}"
                    )
                api_call_start_time = time.time()
                conversation = [{"role": "user", "content": user_input}]
                response_obj = ask_chat_gpt(conversation, gpt_version)
                api_call_end_time = time.time()
                print(
                    f"[green]Answer from ChatGPT: {response_obj['choices'][0]['message']['content']}[/green]"
                )
                send_to_discord(
                    discord_hook,
                    f"Answer from ChatGPT: {response_obj['choices'][0]['message']['content']}",
                )
                response = response_obj["choices"][0]["message"]["content"].strip()
                response = unidecode(response)
                tokens_used = response_obj["usage"]["total_tokens"]
                cost_usd = tokens_used * token_price
                print(f"Tokens used: {tokens_used}")
                print(f"Estimated cost (USD): {cost_usd}")
                with open(answer_file_path, "w") as answer_file:
                    response_no_newlines = response.replace("\n", " ")
                    answer_file.write(response_no_newlines)
                time_taken = api_call_end_time - api_call_start_time
                time_taken = round(time_taken, 2)
                print(f"Time taken (seconds): {time_taken:.2f}")
                os.remove(question_file_path)
        time.sleep(1)

if __name__ == "__main__":
    main()
