# RPMTW-Discord-Bot-python

## Index
- [RPMTW-Discord-Bot-python](#rpmtw-discord-bot-python)
    - [Index](#index)
    - [Pre requirements](#pre-requirements)
    - [Basic setup](#basic-setup)
    - [Deploy](#deploy)
    - [Development](#development)
    - [Features](#features)

## Pre requirements

- **Python** version >= 3.11.x (stable)
    - Unix user can use [pyenv](https://github.com/pyenv/pyenv)
    - Windows user can use [pyenv-win](https://github.com/pyenv-win/pyenv-win) or download from [here](https://www.python.org/downloads/)
- [**Poetry**](https://github.com/python-poetry/poetry) (Package Manager)

## Basic setup

1. **Clone Repo**

    Clone repo to your local machine.


2. **Install Dependencies**

    ```
    poetry install
    ```

    If you want to have a better development experience, it is recommended to use the following commands instead.

    ```
    poetry install --with dev
    ```

3. **Update .env file**

    Insert your discord bot token and universe chat token into [`./.env`](./.env). Sample file can be found at [here](./sample/.env).


Then you can launch bot with following command:

```
poetry shell
python main.py
```

## Deploy

If you want let bot run on production mode, you can add '-P' (which means `production`) to cli args.

```
poetry shell
python main.py -P
```

- This will result in the following changes
    - Keep the log level at `WARNING`
    - Disable debug extra init (won't automatically add `Development` cog)

## Features

- [x] General
    - [x] `hello` - say Hello to user
    - [x] `info` - show bot's information
- [x] Chef
    - [x] `chef user` - chef someone
    - [x] `chef rank` - show chef rank
- [ ] FAQ
    - [ ] `faq <question>` - show the faq
- [x] Dynamic Voice Channel
- [x] Universe Chat
    - [x] Sync message between universe chat and Discord