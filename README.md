# SteamPathFinder
A utility module for finding Steam paths



## Steam Path Finder Module

The Steam Path Finder is a Python module designed to assist in locating the installation path of Steam, the installation paths of specific Steam applications, and the actual paths of specific games on a user's system. This module facilitates programmatic access to Steam games and applications.


## Installation

This documentation assumes that the module is distributed through PyPI. You can install it using the following command:

```command
pip install SteamPathFinder
```


## Basic Usage

Here's how you can use the Steam Path Finder module to find the Steam installation path, the path of a specific Steam application, and the path of a specific game:

```python
from SteamPathFinder import get_steam_path, get_app_path, get_game_path

def main():
    ##  Get the Steam installation path
    steam_path = get_steam_path()
    print(f"Steam path: {steam_path}")
    
    ##  Get the path for a specific application, e.g., a game's app id
    app_id = '1998340'  ##  The app id for the example game.
    game_name = 'Labyrinth of Galleria The Moon Society'  ##  The name of the game folder.

    app_path = get_app_path(steam_path, app_id)
    print(f"Application path: {app_path}")
    
    ##  Get the actual path of a specific game
    game_path = get_game_path(steam_path, app_id, game_name)
    print(f"Game path: {game_path}")

if __name__ == "__main__":
    main()
```

## License

This project is licensed under the MIT License. For more details, see the LICENSE file.
