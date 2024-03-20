from SteamPathFinder import *

# 사용 예시
def main():
    # get_steam_path
    steam_path = get_steam_path()
    print(f"steam_path: {steam_path}")
    
    # get_app_path, game_path
    app_id = '1998340' # 게임의 app id
    game_name = 'Labyrinth of Galleria The Moon Society' # 게임 폴더 이름

    app_path = get_app_path(steam_path, app_id)
    print(f"app_path: {app_path}")
    
    game_path = get_game_path(steam_path, app_id, game_name)
    print(f"game_path: {game_path}")

if __name__ == "__main__":
    main()
