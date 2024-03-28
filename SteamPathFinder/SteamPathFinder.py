import os
import vdf
import winreg

def get_vdf_file_path(steam_path):
    vdf_file_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    
    if not os.path.exists(vdf_file_path):
        raise FileNotFoundError("ERROR: libraryfolders.vdf file does not exist.")
            
    return vdf_file_path

def get_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
    except FileNotFoundError:
        raise FileNotFoundError("ERROR: Steam is not installed.")
    
    if not os.path.exists(steam_path):
        raise FileNotFoundError("ERROR: The Steam path does not exist or is not accessible.")

    return steam_path
    
def get_app_path(steam_path, app_id):
    vdf_file_path = get_vdf_file_path(steam_path)

    try:
        with open(vdf_file_path, 'r') as file:
            data = file.read()
    except Exception as e:
        raise IOError(f"ERROR: Unable to read the libraryfolders.vdf file. {e}")
        
    try:
        parsed = vdf.loads(data)
    except Exception as e:
        raise ValueError(f"ERROR: Error parsing the VDF file. {e}")

    libraryfolders = parsed.get('libraryfolders', {})

    app_path = None

    for folder in libraryfolders.values():
        if isinstance(folder, dict) and 'apps' in folder and str(app_id) in folder['apps']:
            app_path = folder.get('path')
            if app_path and os.path.exists(app_path):  # 경로 존재 여부 확인
                break

    if app_path is None:
        raise FileNotFoundError(f"ERROR: Could not find the installation path for app {app_id}.")
    
    return app_path
    
def get_game_path(steam_path, app_id, game_name):
    app_path = get_app_path(steam_path, app_id)
    game_path = os.path.join(app_path, 'steamapps', 'common', game_name)

    if not os.path.exists(game_path):
        raise FileNotFoundError(f"ERROR: The game path does not exist. Check if the game name '{game_name}' is correct and the game is properly installed.")

    return game_path
