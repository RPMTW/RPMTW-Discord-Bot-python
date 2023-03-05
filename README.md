# RPMTW-Discord-Bot-python

## Index
- [RPMTW-Discord-Bot-python](#rpmtw-discord-bot-python)
  - [Index](#index)
  - [How to setup](#how-to-setup)
  - [Features](#features)

## How to setup

:star: Requirements: Python 3.11 Stable

1. **Install Package Manager**

   1. Windows
      ```ps
      py -3.11 -m pip install pdm
      ```
   2. Linux
      ```hs
      python3.11 -m pip install pdm
      ```

2. **Check PDM Install Success**  
   
   Restart Terminal and run this command
   ```ps
   pdm
   ```

3. **Clone Repo**

   Use Any Github Client (Github Desktop, Gitkraken, etc.) clone repo to local.  
   Or use git command:
   ```bash
   git clone https://github.com/RPMTW/RPMTW-Discord-Bot-python
   ```

4. **Sync Package**
   ```hs
   pdm sync
   ```

5. **Run Script**
   
   1. Windows
      ```hs
      run ./run.bat
      ```
   2. Linux
      ```hs
      start ./run.sh
      ```

## Features

- [x] General
  - [x] `hello` - say Hello to user
  - [x] `info` - show bot's information
- [ ] Chef
  - [ ] `chef user` - chef someone
  - [ ] `chef rank` - show chef rank
- [x] FAQ
  - [x] `faq <question>` - show the faq
- [x] Dynamic Voice Channel
- [ ] Universe Chat
- [ ] ...