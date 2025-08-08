import os
import time
import json
import requests
import pandas as pd

# GENERATE/GET free API Key from https://steamcommunity.com/dev/apikey
API_KEY = "Y0URXXXXAP1XXXXXK3YXXXXXH3R3XXXX" # Replace Y0URXXXXAP1XXXXXK3YXXXXXH3R3XXXX with your own API KEY
LOCAL_CARD_DATA_FILE = "request.php.json" # Delete this file from this folder if you want to fetch latest updated list online.
LONG_PLAYTIME_HOURS = 10 # > 10 hrs considered Long Playtime. Change this as required.

def get_steamid_from_vanity(vanity_url):
    # Converts a Steam custom URL name to a 64-bit SteamID. (https://steamcommunity.com/id/CustomURL/)
    url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={API_KEY}&vanityurl={vanity_url}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('response', {})
        if data.get('success') == 1:
            return data.get('steamid')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error resolving vanity URL: {e}")
        return None

def get_owned_games(steamid):
    # Fetches all owned games for the given SteamID.
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={steamid}&include_appinfo=1&include_played_free_games=1"
    try:
        print("Fetching owned games... (This may take a moment for large libraries)")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('response', {})
        if 'games' in data:
            return data['games']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game list: {e}")
        return None

def fetch_and_cache_card_data():
    # Fetch data from SteamCardExchange Open Api and save it locally.
    try:
        url = "https://www.steamcardexchange.net/api/request.php?GetBoosterPrices"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        card_data = response.json()
        
        with open(LOCAL_CARD_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(card_data, f)
        print(f"Successfully fetched and saved data to '{LOCAL_CARD_DATA_FILE}'.")
        
        data_list = card_data.get('data', [])
        return {str(item[0][0]) for item in data_list}
        
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch master list of card games from API: {e}")
        return set()
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error processing or saving API data: {e}")
        return set()

def get_all_games_with_cards():
    # Fetches a list of all AppIDs that have trading cards.
    if os.path.exists(LOCAL_CARD_DATA_FILE):
        print(f"Local card data file found ('{LOCAL_CARD_DATA_FILE}'). Using local data.")
        try:
            with open(LOCAL_CARD_DATA_FILE, 'r', encoding='utf-8') as f:
                card_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading local file: {e}. Will attempt to fetch from API.")
            return fetch_and_cache_card_data()
    else:
        print(f"No local file found. Fetching master list from SteamCardExchange API...")
        return fetch_and_cache_card_data()

    try:
        data_list = card_data.get('data', [])
        return {str(item[0][0]) for item in data_list}
    except (TypeError, IndexError) as e:
        print(f"Error parsing local card data structure: {e}. It might be corrupted.")
        return set()



def fetch_detailed_game_data(steamid, owned_games, games_with_cards_set):
    # Iterates through each game to fetch detailed card and achievement data.
    detailed_records = []
    total_games = len(owned_games)
    
    print(f"\nFound {total_games} owned games. Fetching detailed data for each...")
    print("(This will be very slow for large libraries, please be patient.)")

    for i, game in enumerate(owned_games):
        appid = game['appid']
        name = game.get('name', 'Unknown Game')
        
        print(f"\t({i+1}/{total_games}) Checking: {name}", end='\r')
        
        card_drops_remaining = "No"
        achievements_status = "Unknown"

        has_trading_cards = "Yes" if str(appid) in games_with_cards_set else "No"
        
        if has_trading_cards == "Yes":
            try:
                card_url = f"https://api.steampowered.com/IPlayerService/GetGameBadgeLevels/v1/?key={API_KEY}&steamid={steamid}&appid={appid}"
                card_resp = requests.get(card_url, timeout=5)
                card_data = card_resp.json().get('response', {})
                if card_data.get('badges') and card_data['badges'][0].get('drops_remaining', 0) > 0:
                    card_drops_remaining = "Yes"
            except Exception:
                pass

        has_stats_flag = game.get('has_community_visible_stats', False)
        if has_stats_flag:
            try:
                ach_url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={API_KEY}&steamid={steamid}&appid={appid}"
                ach_resp = requests.get(ach_url, timeout=5)
                ach_data = ach_resp.json().get('playerstats', {})
                
                if ach_data.get('success') and 'achievements' in ach_data:
                    achievements = ach_data['achievements']
                    total_achievements = len(achievements)
                    unlocked_count = sum(1 for ach in achievements if ach['achieved'] == 1)
                    
                    if total_achievements == 0:
                        achievements_status = "No Achievements"
                    elif unlocked_count == total_achievements:
                        achievements_status = "Completed"
                    elif unlocked_count > 0:
                        achievements_status = "In Progress"
                    else:
                        achievements_status = "Not Started"
                else:
                    achievements_status = "No Achievements"
            except Exception:
                pass
        else:
            achievements_status = "No Achievements"

        record = game.copy()
        record['has_trading_cards'] = has_trading_cards
        record['card_drops_remaining'] = card_drops_remaining
        record['achievements_status'] = achievements_status
        detailed_records.append(record)
        
        time.sleep(1)

    print("\nFinished fetching all detailed data.")
    return detailed_records

def create_dataframe_from_details(detailed_records):
    print("\n--- Compiling Final Report ---")
    final_records = []

    for game in sorted(detailed_records, key=lambda x: x['name']):
        playtime_minutes = game.get('playtime_forever', 0)
        
        if playtime_minutes == 0:
            playtime_category = "Never Played"
        elif playtime_minutes < 60:
            playtime_category = "Short Playtime (< 1 hr)"
        elif playtime_minutes > (LONG_PLAYTIME_HOURS * 60):
            playtime_category = f"Long Playtime (> {LONG_PLAYTIME_HOURS} hrs)"
        else:
            playtime_category = "Played"

        record = {
            "appid": game['appid'],
            "name": game.get('name', 'Unknown Game'),
            "playtime_forever_min": playtime_minutes,
            "playtime_forever_hrs": round(playtime_minutes / 60, 2),
            "playtime_category": playtime_category,
            "has_trading_cards": game['has_trading_cards'],
            "card_drops_remaining": game['card_drops_remaining'],
            "achievements_status": game['achievements_status']
        }
        final_records.append(record)

    return pd.DataFrame(final_records)

def main():
    if API_KEY == "Y0URXXXXAP1XXXXXK3YXXXXXH3R3XXXX" or not API_KEY:
        print("ERROR: Please set your Steam Web API Key in the script.")
        return

    games_with_cards_set = get_all_games_with_cards()
    if not games_with_cards_set:
        print("Warning: Could not get master list of games with cards. Card detection may be incomplete.")

    while True:
        print("https://steamcommunity.com/id/CustomURL/")
        user_input = input("\nEnter your SteamID64 or Custom URL name (or type 'exit' to quit):\n> ")
        
        if user_input.lower() == 'exit':
            break

        steamid = None
        if user_input.isdigit() and len(user_input) == 17:
            steamid = user_input
        else:
            steamid = get_steamid_from_vanity(user_input)
            if steamid:
                print(f"Resolved custom URL '{user_input}' to SteamID64: {steamid}")
            else:
                print(f"ERROR: Could not find a profile for '{user_input}'.")
                continue
        
        owned_games = get_owned_games(steamid)
        if owned_games is None:
            print("\nERROR: Could not retrieve game list. This usually means the profile is set to PRIVATE.\nGo to steam privacy settings and make your profile, playtime, inventory, etc. public and try again in 10 minutes.")
            continue
            
        detailed_game_data = fetch_detailed_game_data(steamid, owned_games, games_with_cards_set)
        df = create_dataframe_from_details(detailed_game_data)
        
        if not df.empty:
            print("\n--- ANALYSIS COMPLETE ---")
            print(f"Total Games Analyzed: {len(df)}")
            print(f"Games with Card Drops Remaining: {len(df[df['card_drops_remaining'] == 'Yes'])}")
            print(f"Games with Achievements 'In Progress': {len(df[df['achievements_status'] == 'In Progress'])}")
            print(f"Games with Achievements 'Not Started': {len(df[df['achievements_status'] == 'Not Started'])}")

            save_file = input("\nSave full analysis to CSV file? (Y/N): ").lower()
            if save_file == 'y':
                filename = f"steam_analysis_{steamid}_{int(time.time())}.csv"
                df.to_csv(filename, index=False)
                print(f"Data saved to {filename}")

if __name__ == "__main__":
    main()