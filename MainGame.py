from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import List, Dict, Optional, Tuple, Any, Union
from Modules.Loader import Write, Read
from Modules.setup import (cEnemy,
                    cWeapon,
                    cEquippableItems,
                    cObject,
                    cDebuff,
                    cShop,
                    cInventory,
                    cIDSorter,
                    setup_player,
                    vInventory,
                    fShop,
                    InventorySorter,
                    enemy_loader)
from Modules.check_admin import main_c
from Modules.ModLoader import get_mod_loader, get_mod_api
from Modules.ModDevTools import main_dev_menu

import random
import time as sp
import keyboard
import os
import sys
from enum import Enum, auto

# Game configuration
CONFIG = {
    "ASK_FOR_ADMIN": True,  # If False (Recommended for Windows): skips the admin perms check

    "COMBAT": {
        "DELAY_BETWEEN_ROUNDS": 0.5,  # Seconds between combat rounds
        "CHANCE_TO_FLEE": 0.3,      # Base chance to successfully flee combat, TODO: Needs revision
    },
    "DISPLAY": {
        "BAR_LENGTH": 25,           # Length of health/mana bars
        "MENU_REFRESH_RATE": 0.5,   # Seconds to wait before refreshing menus
    },
    "DEBUG": {
        "ENABLED": False,           # Enable debug mode, It does nothing
    }
}

# Game state management
class GameState(Enum):
    """Enum to track the current game state"""
    MAIN_MENU = auto()
    EXPLORING = auto()
    COMBAT = auto()
    SHOP = auto()
    INVENTORY = auto()
    STATS = auto()

# Initialize console with custom theme
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "menu_title": "bold yellow",
    "menu_option": "bright_white",
})
console = Console(theme=custom_theme)

# Game state variables
enemies: List[Any] = []
enemy: Optional[cEnemy] = None
chosen_area: Optional[str] = None
shop_objects: List[Any] = []
zone_name: str = ""
tick: int = 0
chars: List[Any] = []
current_state: GameState = GameState.MAIN_MENU

# Run initial admin check
if CONFIG["ASK_FOR_ADMIN"]:
    main_c()
cls = os.system('clear')

def zone_loader(player_zone: str) -> cEnemy:
    """
    Load enemies from the specified zone and select a random one.
    
    Args:
        player_zone: The zone name to load enemies from
        
    Returns:
        A randomly selected enemy from the specified zone
    """
    try:
        # Use os.path.join for cross-platform path handling
        data_path = os.path.join("Data", "DataStats.json")
        data_npcs = Read(data_path, player_zone, None)
        
        if not data_npcs:
            console.print(f"[danger]No se encontraron datos para la zona: {player_zone}[/danger]")
            return None
            
        enemy_list = enemy_loader(data_npcs)
        
        if not enemy_list:
            console.print(f"[danger]No se encontraron enemigos en la zona: {player_zone}[/danger]")
            return None
            
        enemy_random = random.choice(enemy_list)
        console.print(f"[success]Enemigo seleccionado: {enemy_random.NAME}[/success]")
        return enemy_random
    except Exception as e:
        console.print(f"[danger]Error al cargar la zona {player_zone}: {str(e)}[/danger]")
        return None

# Initialize test weapons with proper physical and magical damage parameters
# Parameters: ID, name, physical_dmg_min, physical_dmg_max, magical_dmg_min, magical_dmg_max, Gold_Cost, Description
GreatSword = cWeapon(3, "Espada Grande", 15, 25, 0, 0, 50, "sword ")
MagicStaff = cWeapon(4, "Bastón Mágico", 2, 5, 10, 20, 50, "staff")
ring_as = cEquippableItems(7, "anillo", 5, 0, 0, 0, 40, "Aumenta stats", "Ring")
ring_as2 = cEquippableItems(6, "armadura 2", 5, 0, 0, 0, 40, "Protege", "Armor")
HPPotionL = cObject(5, "Pocion de curacion", 40, 0, 50, "Restaura hp")
weak = cDebuff("algo", ArmorPierce=10)




def display_player_status() -> None:
    """Display formatted player status information in a rich panel"""
    status_text = [
        f"[bold]Nombre:[/bold] {player.name} [dim](Nivel {player.Level})[/dim]",
        f"[bold]EXP:[/bold] {player.EXP}/{player.EXP_M}",
        f"[bold yellow]Oro:[/bold yellow] {player.Gold}",
    ]
    
    if chosen_area is not None:
        status_text.append(f"[bold]Zona actual:[/bold] {chosen_area}")
    
    # Add health and mana bars
    health_bar, health_percent = create_status_bar(player.Health, player.Health_max, "red")
    mana_bar, mana_percent = create_status_bar(player.Mana, player.Mana_max, "blue")
    
    status_text.append(f"[bold red]HP:[/bold red] {health_bar} {health_percent}%")
    status_text.append(f"[bold blue]MP:[/bold blue] {mana_bar} {mana_percent}%")
    
    panel = Panel("\n".join(status_text), title="Estado del Jugador", border_style="bright_white")
    console.print(panel)

player = setup_player()

def create_status_bar(current: float, maximum: float, color: str, return_values: bool = True) -> Union[None, Tuple[str, int]]:
    """
    Create a visual status bar representation for health, mana, etc.
    
    Args:
        current: Current value of the status
        maximum: Maximum possible value
        color: Color to use for the filled portion of the bar
        return_values: Whether to return the bar or print it directly
        
    Returns:
        If return_values is True, returns a tuple with (bar_string, percentage)
        Otherwise, prints the bar and returns None
    """
    # Ensure current doesn't exceed maximum
    current = min(current, maximum)
    # Ensure we don't divide by zero
    if maximum <= 0:
        maximum = 1
        
    bar_length = CONFIG["DISPLAY"]["BAR_LENGTH"]
    filled_length = int(bar_length * current / maximum)
    
    # Create the bar string
    bar = "[" + f"[{color}]#[/{color}]" * filled_length + "-" * (bar_length - filled_length) + "]"
    percentage = int((current / maximum) * 100)
    
    if not return_values:
        console.print(f"Vida: {bar} {percentage}%")
        return None
    
    return bar, percentage




def apply_debuffs(player: Any) -> Dict[str, Any]:
    """
    Apply all active debuffs to the player and return a summary of applied effects.
    
    Args:
        player: The player object to apply debuffs to
        
    Returns:
        A dictionary summarizing all applied debuff effects
    """
    applied_effects = {}
    
    if not hasattr(player, 'applieddebuffs') or not player.applieddebuffs:
        return applied_effects
        
    for debuff in player.applieddebuffs:
        # Get all non-callable, non-dunder attributes
        debuff_attributes = [
            attr for attr in dir(debuff) 
            if not callable(getattr(debuff, attr)) and not attr.startswith("__")
        ]
        
        for debuff_attr in debuff_attributes:
            debuff_value = getattr(debuff, debuff_attr, None)
            if debuff_value is not None:
                # Apply the debuff effect
                debuff.Apply(debuff_attr, player)
                # Record the applied effect
                applied_effects[debuff_attr] = debuff_value
                
    return applied_effects

def display_zone_enemies(zone_name: str, enemies_data: List, strings_data: Dict) -> None:
    """
    Display enemy information for a zone with physical and magical damage.
    
    Args:
        zone_name: Name of the zone to display
        enemies_data: JSON data containing enemy information
        strings_data: String data containing zone description
    """
    zone_title = "Bosque" if "Forest" in zone_name else "Cueva" if "Cave" in zone_name else zone_name
    zone_style = "green" if "Forest" in zone_name or "Bosque" in zone_name else "blue"
    
    zone_table = Table(title=zone_title, title_style=zone_style)
    zone_table.add_column("Enemigo", style=zone_style)
    zone_table.add_column("Vida", justify="right")
    zone_table.add_column("Daño Físico", justify="right", style="red")
    zone_table.add_column("Daño Mágico", justify="right", style="blue")
    zone_table.add_column("Defensa", justify="right")
    
    console.print(f"\n[bold {zone_style}]{zone_title}[/bold {zone_style}]: {strings_data.get('desc', 'No hay descripción disponible')}")
    
    for enemy in enemy_loader(enemies_data, False):
        physical_dmg = f"{enemy.PHYSICAL_DMG_min}-{enemy.PHYSICAL_DMG}"
        magical_dmg = f"{enemy.MAGICAL_DMG_min}-{enemy.MAGICAL_DMG}"
        defense = f"{enemy.DEF}"
        
        zone_table.add_row(
            enemy.NAME,
            str(enemy.HP_M),
            physical_dmg,
            magical_dmg,
            defense
        )
    
    console.print(zone_table)

                

############################## Main Menu Functions ##############################

def display_main_menu() -> None:
    """Display the main game menu with all available options"""
    # Header with title
    console.print(Panel("RPG Game Menu", style="menu_title"))
    
    # Create a table for menu options
    table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    table.add_column("Number", style="menu_option")
    table.add_column("Option", style="menu_option")
    
    # Add menu options
    table.add_row("[1]", "Inspeccionar las zonas")
    table.add_row("[2]", "Ir a una zona")
    table.add_row("[3]", "Tienda")
    table.add_row("[4]", "Inventario")
    table.add_row("[5]", "Usar/equipar objeto")
    table.add_row("[6]", "Pelear")
    table.add_row("[7]", "Mirar Stats")
    table.add_row("[8]", "Gestión de Mods")
    table.add_row("[9]", "Guardar")
    table.add_row("[0]", "Salir del juego")
    
    console.print(table)
    console.print()

def get_validated_input(prompt: str, valid_options: List[int]) -> int:
    """
    Get and validate numeric input from the user.
    
    Args:
        prompt: The prompt to display to the user
        valid_options: List of valid numeric options
        
    Returns:
        The validated integer input
    """
    while True:
        try:
            user_input = input(prompt)
            value = int(user_input)
            
            if value in valid_options:
                return value
            else:
                console.print(f"[warning]Por favor ingresa una opción válida ({', '.join(map(str, valid_options))})[/warning]")
                
        except ValueError:
            console.print("[warning]Por favor ingresa un número válido[/warning]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[info]Saliendo del juego...[/info]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[danger]Error inesperado: {str(e)}[/danger]")

############################## Main Game Loop ##############################

def main():
    """Main game loop function that handles player actions and game state"""
    global chosen_area, tick, enemy, player, current_state
    vInventory.addObject(GreatSword)
    # Apply automatic regeneration and check inventory
    player.Check(vInventory)
    player.Mana = min(player.Mana + player.ManaRegen, player.Mana_max)
    cls
    # Clear the screen for better UI
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Display player status
    display_player_status()
    
    # Display main menu
    display_main_menu()
    
    # Get player choice with validation
    valid_options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    main_input = get_validated_input("Selecciona una opción: ", valid_options)
    
    # Process player choice
    if main_input == 0:
        # Exit game option
        console.print("[info]¿Estás seguro de que quieres salir? (s/n)[/info]")
        confirm = input().lower()
        if confirm == 's' or confirm == 'si':
            console.print("[info]¡Gracias por jugar! Hasta pronto.[/info]")
            sys.exit(0)
    
    elif main_input == 1:
        # Set current state
        current_state = GameState.EXPLORING
        
        try:
            # Use consistent path handling
            data_path = os.path.join("Data", "DataStats.json")
            
            # Create tables for better display of zone information
            console.print(Panel("Información de Zonas", style="menu_title"))
            
            # Forest zone
            enemies_forest = Read(data_path, 'Forest', None)
            forest_strings = Read(data_path, 'Forest', "Strings")
            
            forest_table = Table(title="Bosque", title_style="green")
            forest_table.add_column("Enemigo", style="green")
            forest_table.add_column("Vida", justify="right")
            forest_table.add_column("Daño Físico", justify="right")
            forest_table.add_column("Daño Mágico", justify="right")
            
            console.print(f"\n[bold green]Bosque[/bold green]: {forest_strings.get('desc', 'No hay descripción disponible')}")
            
            for enemy in enemy_loader(enemies_forest, False):
                forest_table.add_row(
                    enemy.NAME, 
                    str(enemy.HP_M), 
                    f"{enemy.PHYSICAL_DMG}/{enemy.PHYSICAL_DMG_min}", 
                    f"{enemy.MAGICAL_DMG}/{enemy.MAGICAL_DMG_min}"
                )
            
            console.print(forest_table)
            
            # Cave zone
            enemies_cave = Read(data_path, 'Cave', None)
            cave_strings = Read(data_path, 'Cave', "Strings")
            
            cave_table = Table(title="Cueva", title_style="blue")
            cave_table.add_column("Enemigo", style="blue")
            cave_table.add_column("Vida", justify="right")
            cave_table.add_column("Daño Físico", justify="right")
            cave_table.add_column("Daño Mágico", justify="right")
            
            console.print(f"\n[bold blue]Cueva[/bold blue]: {cave_strings.get('desc', 'No hay descripción disponible')}")
            
            for enemy in enemy_loader(enemies_cave, False):
                cave_table.add_row(
                    enemy.NAME, 
                    str(enemy.HP_M), 
                    f"{enemy.PHYSICAL_DMG}/{enemy.PHYSICAL_DMG_min}", 
                    f"{enemy.MAGICAL_DMG}/{enemy.MAGICAL_DMG_min}"
                )
            
            console.print(cave_table)
            
        except Exception as e:
            console.print(f"[danger]Error al cargar la información de zonas: {str(e)}[/danger]")
        
        console.print("\n[info]Presiona Enter para continuar... ↵ [/info]")
        keyboard.wait("enter", suppress=True)
    elif main_input == 2:
        # Set current state
        current_state = GameState.EXPLORING
        
        # Create a table for zone selection
        zone_table = Table(title="Selección de Zona", show_header=False)
        zone_table.add_column("Opción", style="bright_white")
        zone_table.add_column("Zona", style="bright_white")
        
        zone_table.add_row("1", "[green]Bosque[/green]")
        zone_table.add_row("2", "[blue]Cueva[/blue]")
        zone_table.add_row("3", "Salir de la zona actual")
        
        console.print(zone_table)
        
        # Get validated zone input
        valid_zones = [1, 2, 3]
        zone_input = get_validated_input("Ingresa la zona a la que quieres ir: ", valid_zones)
        
        if zone_input == 1:
            chosen_area = "[green]Bosque[/green]"
            console.print("[info]Cargando zona de Bosque...[/info]")
            enemy = zone_loader("Forest")
            
            if enemy:
                console.print(f"[success]Has entrado al Bosque. Ten cuidado con {enemy.NAME}![/success]")
            else:
                console.print("[warning]No se pudo cargar un enemigo del Bosque.[/warning]")
                
        elif zone_input == 2:
            chosen_area = "[blue]Cueva[/blue]"
            console.print("[info]Cargando zona de Cueva...[/info]")
            enemy = zone_loader("Cave")
            
            if enemy:
                console.print(f"[success]Has entrado a la Cueva. Ten cuidado con {enemy.NAME}![/success]")
            else:
                console.print("[warning]No se pudo cargar un enemigo de la Cueva.[/warning]")
                
        elif zone_input == 3:
            if chosen_area is not None:
                console.print("[info]Saliendo de la zona actual...[/info]")
                chosen_area = None
                enemy = None
            else:
                console.print("[danger]No puedes irte sin haber escogido una zona antes...[/danger]")
            
        # Pause to read message
        console.print("\n[info]Presiona Enter para continuar... ↵ [/info]")
        keyboard.wait("enter", suppress=True)
            
    elif main_input == 3:
        # Set current state
        current_state = GameState.SHOP
        console.print("[info]Entrando a la tienda...[/info]")
        
        try:
            fShop(player)
        except Exception as e:
            console.print(f"[danger]Error en la tienda: {str(e)}[/danger]")
        
        console.print("\n[info]Presiona Enter para volver al menú principal... ↵ [/info]")
        keyboard.wait("enter", suppress=True)
        current_state = GameState.MAIN_MENU

    elif main_input == 4:
        # Set current state
        current_state = GameState.INVENTORY
        console.print(Panel("Inventario", style="menu_title"))
        
        try:
            player.Check(vInventory)
            vInventory.PrintObjects()
        except Exception as e:
            console.print(f"[danger]Error al mostrar el inventario: {str(e)}[/danger]")
        
        console.print("\n[info]Presiona Enter para volver al menú principal... ↵ [/info]")
        keyboard.wait("enter", suppress=True)
        current_state = GameState.MAIN_MENU

    elif main_input == 5:
        # Set current state
        current_state = GameState.INVENTORY
        console.print(Panel("Usar/Equipar Objetos", style="menu_title"))
        
        try:
            player.Equip(vInventory, InventorySorter, player)
            player.Check(vInventory)
            console.print("[success]Objeto equipado correctamente.[/success]")
        except Exception as e:
            console.print(f"[danger]Error al equipar objeto: {str(e)}[/danger]")
        
        console.print("\n[info]Presiona Enter para volver al menú principal... ↵ [/info]")
        keyboard.wait("enter", suppress=True)
        current_state = GameState.MAIN_MENU

    elif main_input == 6:
        # Handle combat
        if enemy is None:
            console.print("[danger]No has escogido ningún lugar. Debes ir a una zona primero.[/danger]")
            console.print("\n[info]Presiona Enter para volver al menú principal... ↵ [/info]")
            keyboard.wait("enter", suppress=True)
        else:
            # Set current state
            current_state = GameState.COMBAT
            combat_round = 1
            combat_active = True
            
            # Combat loop
            while combat_active:
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Display combat header
                console.print(Panel(f"[bold]Combate - Ronda {combat_round}[/bold]", style="danger"))
                
                # Calculate padding for aligned display
                max_name_length = max(len(player.name), len(enemy.NAME) + 4)
                padding = f"{' ' * (max_name_length - len(player.name))}  |"
                
                # Apply active debuffs
                player_debuffs = apply_debuffs(player)
                if player_debuffs:
                    debuff_text = ", ".join([f"{attr}: {val}" for attr, val in player_debuffs.items()])
                    console.print(f"[warning]Debuffs activos: {debuff_text}[/warning]")
                
                # Combat options
                combat_table = Table(show_header=False, box=None)
                combat_table.add_column("Opción", style="bright_white")
                combat_table.add_column("Acción", style="bright_white")
                
                combat_table.add_row("[1]", "Atacar")
                combat_table.add_row("[2]", "Usar objeto")
                combat_table.add_row("[3]", "Intentar huir")
                
                console.print(combat_table)
                
                # Get combat action
                combat_action = get_validated_input("Elige tu acción: ", [1, 2, 3])
                
                if combat_action == 1:
                    # Player attacks first
                    console.print("\n[bold]¡Tu turno![/bold]")
                    sp.sleep(1)
                    
                    # Player attack
                    damage_dealt = player.attack(enemy)
                    if damage_dealt is not None:
                        console.print(f"[success]¡Has atacado a {enemy.NAME} por {damage_dealt} puntos de daño![/success]")
                    
                    # Check if enemy is defeated
                    if enemy.HP <= 0:
                        console.print(f"[success]¡Has derrotado a {enemy.NAME}![/success]")
                        # Calculate rewards
                        exp_gain = enemy.EXP_TO_PLAYER
                        gold_gain = enemy.GOLD
                        
                        player.EXP += exp_gain
                        player.Gold += gold_gain
                        
                        console.print(f"[success]Ganaste {exp_gain} puntos de experiencia y {gold_gain} de oro.[/success]")
                        
                        # Check for level up
                        if player.EXP >= player.EXP_M:
                            while player.EXP >= player.EXP_M:
                                player.Level += 1
                                player.EXP -= player.EXP_M
                                player.EXP_M = int(player.EXP_M * 1.5)
                                player.Health_max += 20
                                player.Mana_max += 10
                                player.Health = player.Health_max
                                player.Mana = player.Mana_max
                                
                                console.print(f"[success]¡Subiste al nivel {player.Level}![/success]")
                        
                        combat_active = False
                        break
                    
                    # Enemy's turn
                    console.print("\n[bold]¡Turno del enemigo![/bold]")
                    sp.sleep(1)
                    
                    # Enemy attack
                    damage_taken = enemy.attack(player)
                    if damage_taken is not None:
                        console.print(f"[danger]{enemy.NAME} te ha atacado por {damage_taken} puntos de daño![/danger]")
                    
                    # Check if player is defeated
                    if player.Health <= 0:
                        console.print(f"[danger]¡Has sido derrotado por {enemy.NAME}![/danger]")
                        console.print("[danger]Game Over[/danger]")
                        
                        # Restore some health to allow continuing
                        player.Health = max(1, int(player.Health_max * 0.1))
                        combat_active = False
                        break
                
                elif combat_action == 2:
                    # Use object option
                    console.print("[info]Inventario:[/info]")
                    usable_items = []
                    
                    # Display usable items
                    for i, item in enumerate(vInventory.Objects):
                        if hasattr(item, 'isUsable') and item.isUsable:
                            usable_items.append(item)
                            console.print(f"[{i+1}] {item.Name}")
                    
                    if not usable_items:
                        console.print("[warning]No tienes objetos utilizables.[/warning]")
                        sp.sleep(2)
                        continue
                    
                    # Get item selection
                    valid_items = list(range(1, len(usable_items) + 1))
                    item_choice = get_validated_input("Selecciona un objeto para usar (0 para cancelar): ", [0] + valid_items)
                    
                    if item_choice == 0:
                        console.print("[info]Cancelando uso de objeto...[/info]")
                        continue
                    
                    # Use the selected item
                    selected_item = usable_items[item_choice - 1]
                    # Implement item usage logic here
                    console.print(f"[success]Has usado {selected_item.Name}[/success]")
                    
                    # Enemy still gets a turn
                    console.print("\n[bold]¡Turno del enemigo![/bold]")
                    sp.sleep(1)
                    
                    # Enemy attack
                    damage_taken = enemy.attack(player)
                    console.print(f"[danger]{enemy.NAME} te ha atacado por {damage_taken} puntos de daño![/danger]")
                    
                    # Check if player is defeated
                    if player.Health <= 0:
                        console.print(f"[danger]¡Has sido derrotado por {enemy.NAME}![/danger]")
                        console.print("[danger]Game Over[/danger]")
                        
                        # Restore some health to allow continuing
                        player.Health = max(1, int(player.Health_max * 0.1))
                        combat_active = False
                        break
                
                elif combat_action == 3:
                    # Try to flee
                    flee_chance = CONFIG["COMBAT"]["CHANCE_TO_FLEE"]
                    # Increase chance based on player agility if available
                    if hasattr(player, 'AGI'):
                        flee_chance += min(0.4, player.AGI / 100)
                    
                    if random.random() < flee_chance:
                        console.print("[success]¡Has logrado escapar del combate![/success]")
                        combat_active = False
                        break
                    else:
                        console.print("[danger]¡No pudiste escapar![/danger]")
                        
                        # Enemy gets a free attack
                        console.print("\n[bold]¡El enemigo te ataca mientras intentas huir![/bold]")
                        sp.sleep(1)
                        
                        # Enemy attack with bonus damage
                        damage_taken = enemy.attack(player) * 1.2
                        console.print(f"[danger]{enemy.NAME} te ha atacado por {damage_taken} puntos de daño![/danger]")
                        
                        # Check if player is defeated
                        if player.Health <= 0:
                            console.print(f"[danger]¡Has sido derrotado por {enemy.NAME}![/danger]")
                            console.print("[danger]Game Over[/danger]")
                            
                            # Restore some health to allow continuing
                            player.Health = max(1, int(player.Health_max * 0.1))
                            combat_active = False
                            break
                
                # Display updated status after combat round
                print("\n")
                player_hp_bar, player_hp_percent = create_status_bar(player.Health, player.Health_max, "green", True)
                player_mp_bar, player_mp_percent = create_status_bar(player.Mana, player.Mana_max, "blue", True)
                
                enemy_hp_bar, enemy_hp_percent = create_status_bar(enemy.HP, enemy.HP_M, "red", True)
                enemy_mp_bar, enemy_mp_percent = create_status_bar(enemy.MP, enemy.MP_M, "blue", True)
                
                # Create status table
                status_table = Table(show_header=False, box=None)
                status_table.add_column("Entity", style="bright_white")
                status_table.add_column("HP", style="bright_white")
                status_table.add_column("MP", style="bright_white")
                
                status_table.add_row(
                    f"[bold]{player.name}[/bold]", 
                    f"{player_hp_bar} {player_hp_percent}%", 
                    f"{player_mp_bar} {player_mp_percent}%"
                )
                
                status_table.add_row(
                    f"[bold red]{enemy.NAME}[/bold red]", 
                    f"{enemy_hp_bar} {enemy_hp_percent}%", 
                    f"{enemy_mp_bar} {enemy_mp_percent}%"
                )
                
                console.print(status_table)
                
                # Increment combat round
                combat_round += 1
                
                # Delay between rounds
                sp.sleep(CONFIG["COMBAT"]["DELAY_BETWEEN_ROUNDS"])
            
            # Reset state after combat
            current_state = GameState.MAIN_MENU
            console.print("\n[info]Presiona Enter para volver al menú principal... ↵ [/info]")
            keyboard.wait("enter", suppress=True)
    elif main_input == 7:
        # Set current state
        current_state = GameState.STATS
        
        # Create a rich panel for player stats
        stats_lines = [
            f"[bold]Nombre:[/bold] {player.name} - [bold]Nivel:[/bold] {player.Level}",
            "",
            f"[bold red]Vida:[/bold red] [red]{player.Health}/{player.Health_max}[/red]",
            f"[bold blue]Mana:[/bold blue] [blue]{player.Mana}/{player.Mana_max}[/blue] ([cyan]Regen: {player.ManaRegen}[/cyan])",
            "",
            f"[bold]Defensa:[/bold] {player.DEF} puntos / {player.DefensePercentage}%",
            f"[bold]Agilidad:[/bold] {player.AGI}",
            f"[bold]Prob. ContraAtaque:[/bold] {player.CounterAttack}%",
            f"[bold]Prob. Evasion:[/bold] {player.Evasion}%",
            "",
            f"[bold yellow]Oro:[/bold yellow] {player.Gold}",
            f"[bold cyan]Experiencia:[/bold cyan] {player.EXP}/{player.EXP_M}"
        ]
        
        # Add status bars
        health_bar, health_percent = create_status_bar(player.Health, player.Health_max, "red", True)
        mana_bar, mana_percent = create_status_bar(player.Mana, player.Mana_max, "blue", True)
        exp_bar, exp_percent = create_status_bar(player.EXP, player.EXP_M, "green", True)
        
        stats_lines.append("")
        stats_lines.append(f"Salud: {health_bar} {health_percent}%")
        stats_lines.append(f"Mana:  {mana_bar} {mana_percent}%")
        stats_lines.append(f"EXP:   {exp_bar} {exp_percent}%")
        
        # Display equipment if available
        if hasattr(player, 'Equipment'):
            stats_lines.append("")
            stats_lines.append("[bold underline]Equipo actual:[/bold underline]")
            
            for slot, item in player.Equipment.items():
                if item:
                    stats_lines.append(f"[bold]{slot}:[/bold] {item.Name}")
                else:
                    stats_lines.append(f"[bold]{slot}:[/bold] [dim]Vacío[/dim]")
        
        # Create and display the panel
        stats_panel = Panel("\n".join(stats_lines), title="Estadísticas del Jugador", border_style="cyan")
        console.print(stats_panel)
        
        # Wait for user input to continue
        console.print("\n[info]Presiona Enter para volver al menú principal... ↵ [/info]")
        keyboard.wait("enter", suppress=True)
        current_state = GameState.MAIN_MENU
    
    elif main_input == 8:
        # Gestión de Mods
        console.print(Panel(" Gestión de Mods", style="cyan"))
        
        mod_loader_instance = get_mod_loader()
        mod_api_instance = get_mod_api()
        
        while True:
            console.print("\n1.  Mostrar mods cargados")
            console.print("2.  Cargar/Recargar todos los mods")
            console.print("3.  Estado del sistema de mods")
            console.print("0.  Volver al menú principal")
            
            mod_choice = get_validated_input("Selecciona una opción: ", [0, 1, 2, 3])
            
            if mod_choice == 0:
                break
            elif mod_choice == 1:
                mod_loader_instance.display_mods_info()
                
                # Mostrar comandos personalizados si existen
                if mod_api_instance.custom_commands:
                    console.print("\n[bold]Comandos personalizados disponibles:[/bold]")
                    for cmd_name, cmd_info in mod_api_instance.custom_commands.items():
                        console.print(f"• {cmd_name}: {cmd_info.get('description', 'Sin descripción')}")
                
            elif mod_choice == 2:
                console.print("[info]Cargando mods...[/info]")
                mod_loader_instance.load_all_mods()
                console.print("[success]Proceso de carga completado.[/success]")
                
            elif mod_choice == 3:
                console.print(Panel(" Estado del Sistema de Mods", style="green"))
                
                loaded_count = len(mod_loader_instance.loaded_mods)
                console.print(f"Mods cargados: {loaded_count}")
                
                # Estadísticas de la API
                console.print(f"Items registrados: {len(mod_api_instance.registered_items)}")
                console.print(f"Enemigos registrados: {len(mod_api_instance.registered_enemies)}")
                console.print(f"Zonas registradas: {len(mod_api_instance.registered_zones)}")
                console.print(f"Comandos personalizados: {len(mod_api_instance.custom_commands)}")
                console.print(f"Manejadores de eventos: {sum(len(handlers) for handlers in mod_api_instance.event_handlers.values())}")
            
            console.print("\n[info]Presiona Enter para continuar...[/info]")
            keyboard.wait("enter", suppress=True)
        
        current_state = GameState.MAIN_MENU
    
    elif main_input == 9:
        console.print("\n[warning]¿Deseas guardar antes de salir? (s/n)[/warning]")
        save_response = input().lower()  
        if save_response == 's' or save_response == 'si':
            save_game()
                

# Add a save game function
def save_game() -> bool:
    """
    Save the current game state to a file.
    
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Create save data structure
        save_data = {
            "player": {
                "name": player.name,
                "level": player.Level,
                "health": player.Health,
                "health_max": player.Health_max,
                "mana": player.Mana,
                "mana_max": player.Mana_max,
                "exp": player.EXP,
                "exp_max": player.EXP_M,
                "gold": player.Gold
            },
            "game_state": {
                "area": chosen_area,
                "tick": tick
            },
            "timestamp": str(sp.time())
        }
        
        # Write save data to file
        Write("./Data/SaveGame.json", save_data)
        console.print("[success]Juego guardado correctamente.[/success]")
        return True
    except Exception as e:
        console.print(f"[danger]Error al guardar el juego: {str(e)}[/danger]")
        return False

# Add a load game function
def load_game() -> bool:
    """
    Load a saved game from file.
    
    Returns:
        True if load was successful, False otherwise
    """
    global player, chosen_area, tick
    
    try:
        # Check if save file exists
        if not os.path.exists("./Data/SaveGame.json"):
            console.print("[warning]No hay partidas guardadas.[/warning]")
            return False
        
        # Load save data
        save_data = Read("./Data/SaveGame.json", None, None)
        
        if not save_data:
            console.print("[warning]Archivo de guardado vacío o corrupto.[/warning]")
            return False
        
        # Restore player state
        player_data = save_data.get("player", {})
        game_state = save_data.get("game_state", {})
        
        # Restore basic player attributes
        player.name = player_data.get("name", player.name)
        player.Level = player_data.get("level", player.Level)
        player.Health = player_data.get("health", player.Health)
        player.Health_max = player_data.get("health_max", player.Health_max)
        player.Mana = player_data.get("mana", player.Mana)
        player.Mana_max = player_data.get("mana_max", player.Mana_max)
        player.EXP = player_data.get("exp", player.EXP)
        player.EXP_M = player_data.get("exp_max", player.EXP_M)
        player.Gold = player_data.get("gold", player.Gold)
        
        # Restore game state
        chosen_area = game_state.get("area", None)
        tick = game_state.get("tick", 0)
        
        console.print("[success]Partida cargada correctamente.[/success]")
        return True
    except Exception as e:
        console.print(f"[danger]Error al cargar la partida: {str(e)}[/danger]")
        return False

# Game initialization function
def init_game():
    """Initialize the game and display welcome message"""
    console.print(Panel("Bienvenido al Juego RPG", style="success"))
    console.print("[info]Iniciando juego...[/info]")
    
    # Cargar mods automáticamente
    try:
        console.print("[info]Inicializando sistema de mods...[/info]")
        mod_loader_instance = get_mod_loader()
        mod_loader_instance.load_all_mods()
    except Exception as e:
        console.print(f"[warning]Error al cargar mods: {str(e)}[/warning]")
    
    # Check for saved games
    if os.path.exists("./Data/SaveGame.json"):
        console.print("[info]Se ha encontrado una partida guardada.[/info]")
        console.print("¿Deseas cargar la partida guardada? (s/n)")
        response = input().lower()
        
        if response == 's' or response == 'si':
            load_game()

# Main game execution
if __name__ == "__main__":
    try:
        # Initialize game
        init_game()
        
        # Main game loop
        while True:
            try:
                main()
            except Exception as e:
                console.print(f"[danger]Error en el bucle principal: {str(e)}[/danger]")
                console.print("[info]El juego intentará continuar...[/info]")
                sp.sleep(2)
    except Exception as e:
        console.print(f"[danger]Error crítico: {str(e)}[/danger]")
        console.print("[danger]El juego se cerrará.[/danger]")
        sys.exit(1)


