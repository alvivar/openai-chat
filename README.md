# chat.py

A simple continuous chat with OpenAI GPT3 and GPT4.

    usage: chat.py [-h] [--gpt4] [--clean] [prompt_file ...]

    positional arguments:
    prompt_file  System prompt file

    options:
    -h, --help   show this help message and exit
    --gpt4       Use GPT-4 instead of GPT-3.5 Turbo
    --clean      Ignore previous messages

## To do

-   Different conversations on different logs
-   Handle OpenAI API errors
-   ENV stuff instead of keys.txt by default
-   Prompt should be an argument (?)
-   Support other engines by argument
