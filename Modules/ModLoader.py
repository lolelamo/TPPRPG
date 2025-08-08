import os
import sys
import importlib
import importlib.util
import json
import inspect
from typing import Dict, List, Any, Optional, Callable, Type
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging

# Configurar logging específico para mods
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='tpprpg_mods.log',
    filemode='a'
)
logger = logging.getLogger('TPPRPG.ModLoader')

console = Console()

class ModAPI:

    def __init__(self):
        self.registered_items = {}
        self.registered_enemies = {}
        self.registered_zones = {}
        self.event_handlers = {}
        self.custom_commands = {}
        self.registered_shops = {}
        
    def register_item(self, item_class, item_data):
        """Registra un nuevo item en el juego"""
        item_id = item_data.get('id', f'mod_item_{len(self.registered_items)}')
        self.registered_items[item_id] = {
            'class': item_class,
            'data': item_data
        }
        logger.info(f"Item registrado: {item_id}")
        
    def register_enemy(self, enemy_class, enemy_data):
        """Registra un nuevo enemigo en el juego"""
        enemy_id = enemy_data.get('id', f'mod_enemy_{len(self.registered_enemies)}')
        self.registered_enemies[enemy_id] = {
            'class': enemy_class,
            'data': enemy_data
        }
        logger.info(f"Enemigo registrado: {enemy_id}")
        
    def register_zone(self, zone_name, zone_data):
        """Registra una nueva zona en el juego"""
        self.registered_zones[zone_name] = zone_data
        logger.info(f"Zona registrada: {zone_name}")
        
    def register_event_handler(self, event_name, handler_func):
        """Registra un manejador de eventos"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler_func)
        logger.info(f"Event handler registrado para: {event_name}")
        
    def register_command(self, command_name, handler_func, description=""):
        """Registra un comando personalizado"""
        self.custom_commands[command_name] = {
            'handler': handler_func,
            'description': description
        }
        logger.info(f"Comando registrado: {command_name}")
        
    def register_shop(self, shop_name, shop_data):
        """Registra una nueva tienda"""
        self.registered_shops[shop_name] = shop_data
        logger.info(f"Tienda registrada: {shop_name}")
        
    def fire_event(self, event_name, *args, **kwargs):
        """Dispara un evento para todos los manejadores registrados"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error en event handler {handler.__name__}: {e}")

class ModInfo:
    """Información sobre un mod cargado"""
    def __init__(self, mod_id, name, version, author, description, file_path):
        self.mod_id = mod_id
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.file_path = file_path
        self.loaded = False
        self.enabled = True

class ModLoader:
    """
    Cargador principal de mods - Similar al sistema de Forge
    """
    def __init__(self, mods_directory="mods"):
        self.mods_directory = Path(mods_directory)
        self.loaded_mods = {}
        self.mod_api = ModAPI()
        self.mod_configs = {}
        
        # Crear directorio de mods si no existe
        self.mods_directory.mkdir(exist_ok=True)
        self._create_example_mod_structure()
        
    def _create_example_mod_structure(self):
        """Crea la estructura de ejemplo para desarrollar mods"""
        example_dir = self.mods_directory / "example_mod"
        example_dir.mkdir(exist_ok=True)
        
        # Crear mod.json de ejemplo
        example_mod_info = {
            "mod_id": "example_mod",
            "name": "Mod de Ejemplo",
            "version": "1.0.0",
            "author": "Tu Nombre",
            "description": "Un mod de ejemplo para mostrar cómo crear mods",
            "main": "main.py",
            "dependencies": [],
            "game_version": "1.0.0"
        }
        
        mod_info_path = example_dir / "mod.json"
        if not mod_info_path.exists():
            with open(mod_info_path, 'w', encoding='utf-8') as f:
                json.dump(example_mod_info, f, indent=4, ensure_ascii=False)
        
        # Crear main.py de ejemplo
        main_py_path = example_dir / "main.py"
        if not main_py_path.exists():
            example_code = '''"""
Mod de ejemplo para TPPRPG
Este es un template básico que muestra cómo crear mods
"""

from Modules.setup import cWeapon, cEnemy, cEquippableItems

def init_mod(api):
    """
    Función principal que se llama cuando el mod se carga
    """
    print(f"[green]Cargando mod: {get_mod_info()['name']}[/green]")
    
    # Registrar nuevos items
    register_items(api)
    
    # Registrar nuevos enemigos
    register_enemies(api)
    
    # Registrar manejadores de eventos
    register_events(api)
    
    # Registrar comandos personalizados
    register_commands(api)

def get_mod_info():
    """Información del mod"""
    return {
        "name": "Mod de Ejemplo",
        "version": "1.0.0",
        "author": "Tu Nombre"
    }

def register_items(api):
    """Registra nuevos items del mod"""
    
    # Ejemplo: Espada mágica
    magic_sword_data = {
        'id': 'magic_sword',
        'name': 'Espada Mágica',
        'physical_dmg_min': 20,
        'physical_dmg_max': 35,
        'magical_dmg_min': 10,
        'magical_dmg_max': 20,
        'gold_cost': 150,
        'description': 'Una espada imbuida con magia elemental'
    }
    
    # Crear la clase del item
    magic_sword = cWeapon(
        ID=1001,  # IDs de mods empiezan en 1000+
        name=magic_sword_data['name'],
        physical_dmg_min=magic_sword_data['physical_dmg_min'],
        physical_dmg_max=magic_sword_data['physical_dmg_max'],
        magical_dmg_min=magic_sword_data['magical_dmg_min'],
        magical_dmg_max=magic_sword_data['magical_dmg_max'],
        Gold_Cost=magic_sword_data['gold_cost'],
        Description=magic_sword_data['description']
    )
    
    api.register_item(cWeapon, magic_sword_data)

def register_enemies(api):
    """Registra nuevos enemigos del mod"""
    
    dragon_data = {
        'id': 'fire_dragon',
        'NAME': 'Dragón de Fuego',
        'HP_M': 200,
        'PHYSICAL_DMG': 40,
        'MAGICAL_DMG': 30,
        'PHYSICAL_DMG_min': 25,
        'MAGICAL_DMG_min': 15,
        'MP_M': 100,
        'EXP_TO_PLAYER': 150,
        'DEF': 20,
        'LS': 5,
        'DBUFF_TO_PLAYER': [],
        'BUFF_RECEIVED': [],
        'GOLD': 200,
        'zone': 'dragon_lair'
    }
    
    api.register_enemy(cEnemy, dragon_data)

def register_events(api):
    """Registra manejadores de eventos"""
    
    def on_player_level_up(player):
        print(f"[cyan]¡{player.name} subió de nivel! Nivel actual: {player.Level}[/cyan]")
        # Dar bonus especial cada 5 niveles
        if player.Level % 5 == 0:
            player.Gold += 50
            print("[yellow]¡Bonus de oro por múltiplo de 5 niveles![/yellow]")
    
    def on_enemy_defeated(player, enemy):
        print(f"[green]¡{enemy.NAME} derrotado por el mod de ejemplo![/green]")
    
    api.register_event_handler('player_level_up', on_player_level_up)
    api.register_event_handler('enemy_defeated', on_enemy_defeated)

def register_commands(api):
    """Registra comandos personalizados"""
    
    def magic_heal_command(player):
        heal_amount = 50
        player.Health = min(player.Health + heal_amount, player.Health_max)
        print(f"[green]¡Magia curativa! Restauraste {heal_amount} puntos de vida![/green]")
        return True
    
    api.register_command('curar_magico', magic_heal_command, 
                        "Cura al jugador usando magia (comando del mod de ejemplo)")

# Función de limpieza (opcional)
def cleanup_mod():
    """Se llama cuando el mod se descarga"""
    print("Limpiando recursos del mod de ejemplo...")
'''
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(example_code)
        
        # Crear README para el mod de ejemplo
        readme_path = example_dir / "README.md"
        if not readme_path.exists():
            readme_content = """# Mod de Ejemplo para TPPRPG

Este es un mod de ejemplo que muestra cómo crear mods para TPPRPG.

## Estructura del Mod

- `mod.json`: Información del mod
- `main.py`: Código principal del mod
- `README.md`: Este archivo

## Desarrollo

Para crear tu propio mod:

1. Copia esta carpeta con un nuevo nombre
2. Modifica `mod.json` con la información de tu mod
3. Edita `main.py` con tu código personalizado
4. ¡Disfruta desarrollando!

## API Disponible

- `api.register_item()`: Registra nuevos items
- `api.register_enemy()`: Registra nuevos enemigos
- `api.register_zone()`: Registra nuevas zonas
- `api.register_event_handler()`: Maneja eventos del juego
- `api.register_command()`: Añade comandos personalizados
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

    def discover_mods(self):
        """Descubre todos los mods en el directorio de mods"""
        discovered_mods = {}
        
        for mod_dir in self.mods_directory.iterdir():
            if not mod_dir.is_dir():
                continue
                
            mod_info_file = mod_dir / "mod.json"
            if not mod_info_file.exists():
                logger.warning(f"Mod directory {mod_dir.name} missing mod.json")
                continue
                
            try:
                with open(mod_info_file, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                
                mod_info = ModInfo(
                    mod_id=mod_data.get('mod_id', mod_dir.name),
                    name=mod_data.get('name', mod_dir.name),
                    version=mod_data.get('version', '1.0.0'),
                    author=mod_data.get('author', 'Unknown'),
                    description=mod_data.get('description', ''),
                    file_path=mod_dir
                )
                
                discovered_mods[mod_info.mod_id] = mod_info
                
            except Exception as e:
                logger.error(f"Error loading mod info from {mod_dir}: {e}")
                continue
        
        return discovered_mods

    def load_mod(self, mod_info: ModInfo):
        """Carga un mod específico"""
        try:
            main_file = mod_info.file_path / "main.py"
            if not main_file.exists():
                logger.error(f"Mod {mod_info.mod_id} missing main.py")
                return False
            
            # Crear spec del módulo
            spec = importlib.util.spec_from_file_location(
                f"mod_{mod_info.mod_id}", 
                main_file
            )
            
            if spec is None:
                logger.error(f"Could not create spec for mod {mod_info.mod_id}")
                return False
            
            # Cargar el módulo
            mod_module = importlib.util.module_from_spec(spec)
            sys.modules[f"mod_{mod_info.mod_id}"] = mod_module
            spec.loader.exec_module(mod_module)
            
            # Llamar a la función de inicialización del mod
            if hasattr(mod_module, 'init_mod'):
                mod_module.init_mod(self.mod_api)
            
            mod_info.loaded = True
            self.loaded_mods[mod_info.mod_id] = {
                'info': mod_info,
                'module': mod_module
            }
            
            console.print(f"[green]✓ Mod cargado: {mod_info.name} v{mod_info.version}[/green]")
            logger.info(f"Successfully loaded mod: {mod_info.mod_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading mod {mod_info.mod_id}: {e}")
            console.print(f"[red]✗ Error cargando mod {mod_info.name}: {e}[/red]")
            return False

    def load_all_mods(self):
        """Carga todos los mods disponibles"""
        console.print(Panel("Cargando Mods", style="cyan"))
        
        discovered_mods = self.discover_mods()
        
        if not discovered_mods:
            console.print("[yellow]No se encontraron mods para cargar[/yellow]")
            return
        
        loaded_count = 0
        for mod_id, mod_info in discovered_mods.items():
            if mod_info.enabled and self.load_mod(mod_info):
                loaded_count += 1
        
        console.print(f"[green]Cargados {loaded_count} de {len(discovered_mods)} mods[/green]")

    def get_loaded_mods_info(self):
        """Retorna información de todos los mods cargados"""
        return [mod_data['info'] for mod_data in self.loaded_mods.values()]

    def unload_mod(self, mod_id):
        """Descarga un mod específico"""
        if mod_id not in self.loaded_mods:
            return False
        
        mod_data = self.loaded_mods[mod_id]
        mod_module = mod_data['module']
        
        # Llamar función de limpieza si existe
        if hasattr(mod_module, 'cleanup_mod'):
            try:
                mod_module.cleanup_mod()
            except Exception as e:
                logger.error(f"Error in cleanup for mod {mod_id}: {e}")
        
        # Remover del sistema de módulos
        if f"mod_{mod_id}" in sys.modules:
            del sys.modules[f"mod_{mod_id}"]
        
        del self.loaded_mods[mod_id]
        console.print(f"[yellow]Mod descargado: {mod_data['info'].name}[/yellow]")
        return True

    def display_mods_info(self):
        """Muestra información de todos los mods cargados"""
        if not self.loaded_mods:
            console.print("[yellow]No hay mods cargados[/yellow]")
            return
        
        table = Table(title="Mods Cargados")
        table.add_column("Nombre", style="cyan")
        table.add_column("Versión", style="magenta")
        table.add_column("Autor", style="green")
        table.add_column("Descripción", style="white")
        
        for mod_data in self.loaded_mods.values():
            mod_info = mod_data['info']
            table.add_row(
                mod_info.name,
                mod_info.version,
                mod_info.author,
                mod_info.description[:50] + "..." if len(mod_info.description) > 50 else mod_info.description
            )
        
        console.print(table)

# Instancia global del cargador de mods
mod_loader = ModLoader()

def get_mod_api():
    """Retorna la instancia de la API de mods"""
    return mod_loader.mod_api

def get_mod_loader():
    """Retorna la instancia del cargador de mods"""
    return mod_loader
