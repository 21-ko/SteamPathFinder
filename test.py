from SteamPathFinder import get_app_path, get_game_path, get_steam_path


def main():
    steam_path = get_steam_path()
    print("steam_path:", steam_path)

    app_id = "1998340"
    app_path = get_app_path(steam_path, app_id)
    print("app_path:", app_path)

    game_path = get_game_path(steam_path, app_id)
    print("game_path:", game_path)


if __name__ == "__main__":
    main()
