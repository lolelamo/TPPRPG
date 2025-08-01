# TPPRPG Game

## Overview
TPPRPG is a text-based role-playing game (RPG) built in Python.

## Project Structure
```
TPPRPG
├── MainGame.py          # Main entry point of the game
├── Modules              # Contains various modules for game functionality
│   ├── Loader.py        # Functions for reading and writing game data
│   ├── setup.py         # Classes and functions for setting up game entities
│   ├── check_admin.py   # Functions to check for administrative permissions
│   └── __init__.py      # Marks the Modules directory as a package
├── Data                 # Contains game data files
│   ├── DataStats.json   # JSON data for game statistics and enemy attributes
│   └── SaveGame.json    # Stores the current game state
├── requirements.txt     # Lists Python dependencies
└── README.md            # Documentation for the project
```

## Installation
1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

## Usage
To start the game, run the `MainGame.py` file:
```
python MainGame.py
```

## Gameplay
- Players can explore different zones, each with unique enemies and challenges.
- Combat mechanics allow players to attack enemies, use items, and attempt to flee.
- Players can manage their inventory and equip items to enhance their abilities.
- The game supports saving and loading progress through the `SaveGame.json` file.

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests to improve the game.

## License
This project is open-source and available under the MIT License.