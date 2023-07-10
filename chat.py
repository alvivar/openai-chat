import argparse
import json
import os

import openai
import pyperclip  # type: ignore
from colorama import Fore  # type: ignore


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
KEYS_PATH = os.path.join(BASE_PATH, "keys.txt")
FULL_PATH = os.path.join(BASE_PATH, "log.full.json")
LAST_PATH = os.path.join(BASE_PATH, "log.last.json")

MAX_TOKENS = 1024
TEMPERATURE = 1.5

ENGINE = {"gpt4": "gpt-4", "gpt3": "gpt-3.5-turbo"}
KEYWORDS = ["as an ai", "as an artificial", "as a language", "can't", "cannot"]
DEFAULT_PROMPT = "Consider previous messages in your answers. Match the user personality. Don't complain."


def load_environment_keys():
    """
    Expecting a file with content like this:

    OPENAI_ORGANIZATION=org-aQ975daacbuA9nbD
    OPENAI_API_KEY=sk-jOaNijiBAR1lWV9pKn6IuB8MIHT0p38R
    """
    with open(KEYS_PATH, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value

def read_prompt_or(filename, default):
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return " ".join(file.read().split())
    else:
        return default

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []

def dump_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)

def input_you():
    return input(f"{Fore.YELLOW}\n\nYou: ")

def print_you(content):
    print(f"{Fore.YELLOW}\n\nYou: {content}")

def print_assistant(content):
    print(f"{Fore.BLUE}\n\n{content}")

def filter_unwanted(messages):
    return [
        x for x in messages
        if x["role"] == "user" or
           x["role"] == "assistant" and not any(k in x["content"].lower() for k in KEYWORDS)
    ]

def openai_initialize():
    openai.organization = os.environ["OPENAI_ORGANIZATION"]
    openai.api_key = os.environ["OPENAI_API_KEY"]

def openai_response(engine, messages):
    return openai.ChatCompletion.create(
        model=engine,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )


def main(args):
    load_environment_keys()
    openai_initialize()

    system_content = read_prompt_or(" ".join(args.prompt_file), DEFAULT_PROMPT)
    engine = ENGINE["gpt4"] if args.gpt4 else ENGINE["gpt3"]

    print(f"{Fore.MAGENTA}\nchat.py powered by {engine.upper()}")
    print(f"System prompt: \"{system_content}\"")

    messages = []
    if not args.clean and os.path.isfile(FULL_PATH):
        messages = load_json(FULL_PATH)

    for msg in messages[-10:]:
        if msg["role"] == "user":
            print_you(f"{msg['content']}")
        elif msg["role"] == "assistant":
            print_assistant(f"{msg['content']}")

    while True:
        user_input = input_you()

        messages.append({"role": "user", "content": user_input})
        filtered = filter_unwanted(messages)[-4:]
        filtered.insert(0, {"role": "system", "content": system_content})

        dump_json(LAST_PATH, filtered)

        response = openai_response(engine, filtered)
        assistant_reply = response['choices'][0]['message']['content'].strip()
        pyperclip.copy(assistant_reply)
        messages.append({"role": "assistant", "content": assistant_reply})

        dump_json(FULL_PATH, messages)

        if any(k in assistant_reply.lower() for k in KEYWORDS):
            assistant_reply = "..."

        print_assistant(f"{assistant_reply}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_file", nargs="*", help="System prompt file")
    parser.add_argument("--gpt4", action="store_const", const=True, help="Use GPT-4 instead of GPT-3.5 Turbo")
    parser.add_argument("--clean", action="store_const", const=True, help="Ignore previous messages")
    args = parser.parse_args()

    main(args)
