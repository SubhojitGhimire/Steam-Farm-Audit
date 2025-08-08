# SteamFarmAudit - Steam Game App ID Extractor for Achievements and Trading Card Farming

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A powerful Python script to analyse your public Steam library, identify remaining trading card drops, track achievement progress, and categorise your games for better backlog management.

---

## Key Features
- Complete Library Analysis: Fetches every game associated with a public Steam profile.
- Accurate Card Drop Detection:
  - Checks which of your games have trading cards available.
  - Accurately determines if you have any card drops remaining for each specific game.
  - Automatically caches the master list of card-eligible games for significantly faster subsequent runs.
- Detailed Achievement Tracking: Checks and categorizes the achievement status for each game (Completed, In Progress, Not Started, or No Achievements).
- Smart Playtime Categorization: Sorts games into useful categories like "Never Played", "Short Playtime", and "Long Playtime".
- Flexible Input: Accepts either your 64-bit SteamID or your custom profile URL name.
- CSV Export: Saves the complete analysis to a timestamped .csv file for easy viewing, sorting, and personal tracking.

## Requirements and Configuration
```
pandas==1.5.3
requests==2.32.4
```

Steam Web API Key: This is required to make requests to Steam's servers.
```
Get your free key here: https://steamcommunity.com/dev/apikey
```

Open the SGAID.py script in a text editor and configure the API variable at the top of the file:
```
PASTE YOUR STEAM WEB API KEY HERE
API_KEY = "Y0URXXXXAP1XXXXXK3YXXXXXH3R3XXXX"
```

## Usage

Download and Unzip this repository OR ```git clone https://github.com/SubhojitGhimire/Steam-Farm-Audit/```

Open a terminal or command prompt in this folder.

Run the script using Python:
```bash
python SGAID.py
```

The script will prompt you to enter your SteamID64 (e.g., 76561198273076433) or your Custom URL Name (the part that comes after /id/ in your profile link, e.g., gabelogannewell).

Be patient! The first run will be slow as it fetches detailed data for every game. Subsequent runs will be much faster thanks to local caching of the trading card list.

Once the analysis is complete, you will see a summary in the terminal and be prompted to save the full results to a CSV file.

## Acknowledgements
1. This tool is powered by the official Steam Web API.
2. Trading card data is sourced from the public API provided by SteamCardExchange.net.

<h1></h1>

**This README.md file has been improved for overall readability (grammar, sentence structure, and organization) using AI tools.*