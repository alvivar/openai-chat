# chat.py

A simple continuous chat with OpenAI GPT3 and GPT4.

    usage: chat.py [-h] [--gpt4] [--clean] [prompt_file ...]

    positional arguments:
    prompt_file  System prompt file

    options:
    -h, --help   show this help message and exit
    --gpt4       Use GPT-4 instead of GPT-3.5 Turbo
    --clean      Ignore previous messages

## Auth

-   Expecting a file named {KEYS_FILE} with content like this, every line in
    this file gets transformed into an environmental variable.

    OPENAI_ORGANIZATION=org-aQ975daacbuA9nbD
    OPENAI_API_KEY=sk-jOaNijiBAR1lWV9pKn6IuB8MIHT0p38R

## To do

-   Different conversations on different logs
-   An argument should represent the amount of previous messages sent to give more contexts
-   Handle OpenAI API errors
-   Prompt should be an argument (?)
-   Support other engines by argument
-   ENV stuff instead of keys.txt by default
