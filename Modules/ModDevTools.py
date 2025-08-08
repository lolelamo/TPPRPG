

import os
import json
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

class ModDevKit:
    """Kit de desarrollo de mods para TPPRPG"""
    
    def __init__(self):
        self.mods_directory = Path("mods")
        self.templates_directory = Path("mod_templates")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crea los directorios necesarios"""
        self.mods_directory.mkdir(exist_ok=True)
        self.templates_directory.mkdir(exist_ok=True)
    
    def create_new_mod(self):
        """ Simple Mod Maker v0.1"""
        console.print(Panel("Creador de Mods TPPRPG", style="cyan"))
        
        # Recopilar información del mod
        mod_id = Prompt.ask("ID del mod (sin espacios)", default="mi_mod")
        mod_name = Prompt.ask("Nombre del mod", default="Mi Increíble Mod")
        mod_version = Prompt.ask("Versión", default="1.0.0")
        mod_author = Prompt.ask("Autor", default="Tu Nombre")
        mod_description = Prompt.ask("Descripción", default="Un mod increíble para TPPRPG")
        
        # Opciones
        console.print("\n[cyan]¿Qué quiere añadir tu mod?[/cyan]")
        add_items = Confirm.ask("¿Nuevos items/armas?", default=True)
        add_enemies = Confirm.ask("¿Nuevos enemigos?", default=True)
        add_zones = Confirm.ask("¿Nuevas zonas?", default=False)
        add_commands = Confirm.ask("¿Comandos personalizados?", default=False)
        add_events = Confirm.ask("¿Manejadores de eventos?", default=False)
        
        # Crear el mod
        mod_data = {
            'mod_id': mod_id,
            'name': mod_name,
            'version': mod_version,
            'author': mod_author,
            'description': mod_description,
            'features': {
                'items': add_items,
                'enemies': add_enemies,
                'zones': add_zones,
                'commands': add_commands,
                'events': add_events
            }
        }
        
        if self._create_mod_structure(mod_data):
            console.print(f"[green]✓ Mod '{mod_name}' creado exitosamente![/green]")
            console.print(f"[yellow]Directorio: mods/{mod_id}[/yellow]")
            console.print("[cyan]Ya puedes empezar a desarrollar tu mod editando main.py[/cyan]")
        else:
            console.print("[red]✗ Error creando el mod[/red]")
    
    def _create_mod_structure(self, mod_data):
        """Crea la estructura del mod basada en los datos proporcionados"""
        try:
            mod_dir = self.mods_directory / mod_data['mod_id']
            
            # Verificar si ya existe
            if mod_dir.exists():
                if not Confirm.ask(f"El mod '{mod_data['mod_id']}' ya existe. ¿Sobrescribir?"):
                    return False
                shutil.rmtree(mod_dir)
            
            mod_dir.mkdir(exist_ok=True)
            
            # Crear mod.json
            mod_info = {
                "mod_id": mod_data['mod_id'],
                "name": mod_data['name'],
                "version": mod_data['version'],
                "author": mod_data['author'],
                "description": mod_data['description'],
                "main": "main.py",
                "dependencies": [],
                "game_version": "1.0.0"
            }
            
            with open(mod_dir / "mod.json", 'w', encoding='utf-8') as f:
                json.dump(mod_info, f, indent=4, ensure_ascii=False)
            
            # Crear main.py personalizado
            main_content = self._generate_main_py(mod_data)
            with open(mod_dir / "main.py", 'w', encoding='utf-8') as f:
                f.write(main_content)
            
            # Crear README.md
            readme_content = self._generate_readme(mod_data)
            with open(mod_dir / "README.md", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Crear assets directory para recursos
            assets_dir = mod_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Crear config directory
            config_dir = mod_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Crear archivo de configuración del mod
            if mod_data['features']['items'] or mod_data['features']['enemies']:
                config_content = self._generate_config_json(mod_data)
                with open(config_dir / "config.json", 'w', encoding='utf-8') as f:
                    json.dump(config_content, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error creando el mod: {e}[/red]")
            return False
    
    def _generate_main_py(self, mod_data):
        """Genera el contenido de main.py basado en las características seleccionadas"""
        content = f'''"""
{mod_data['name']} v{mod_data['version']}
Creado por: {mod_data['author']}

{mod_data['description']}
"""

import json
from pathlib import Path
from Modules.setup import cWeapon, cEnemy, cEquippableItems, cObject

# Cargar configuración del mod
CONFIG_PATH = Path(__file__).parent / "config" / "config.json"

def load_config():
    """Carga la configuración del mod"""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando configuración: {{e}}")
    return {{}}

def init_mod(api):
    """
    Función principal que se llama cuando el mod se carga
    """
    print(f"[green] Cargando {mod_data['name']} v{mod_data['version']}[/green]")
    
    config = load_config()
    
'''
        
        if mod_data['features']['items']:
            content += '''    # Registrar nuevos items
    register_items(api, config)
    
'''
        
        if mod_data['features']['enemies']:
            content += '''    # Registrar nuevos enemigos
    register_enemies(api, config)
    
'''
        
        if mod_data['features']['zones']:
            content += '''    # Registrar nuevas zonas
    register_zones(api, config)
    
'''
        
        if mod_data['features']['events']:
            content += '''    # Registrar manejadores de eventos
    register_events(api)
    
'''
        
        if mod_data['features']['commands']:
            content += '''    # Registrar comandos personalizados
    register_commands(api)
    
'''
        
        content += '''    print(f"[green] {get_mod_info()['name']} cargado exitosamente![/green]")

def get_mod_info():
    """Información del mod"""
    return {
        "name": "''' + mod_data['name'] + '''",
        "version": "''' + mod_data['version'] + '''",
        "author": "''' + mod_data['author'] + '''"
    }

'''
        
        if mod_data['features']['items']:
            content += '''def register_items(api, config):
    """Registra nuevos items del mod"""
    
    items_config = config.get('items', {})
    
    # Ejemplo de espada personalizada
    for item_id, item_data in items_config.items():
        if item_data.get('type') == 'weapon':
            weapon = cWeapon(
                ID=item_data.get('id', 1000),
                name=item_data.get('name', 'Arma Personalizada'),
                physical_dmg_min=item_data.get('physical_dmg_min', 10),
                physical_dmg_max=item_data.get('physical_dmg_max', 20),
                magical_dmg_min=item_data.get('magical_dmg_min', 0),
                magical_dmg_max=item_data.get('magical_dmg_max', 0),
                Gold_Cost=item_data.get('gold_cost', 100),
                Description=item_data.get('description', 'Un arma creada por un mod')
            )
            
            api.register_item(cWeapon, item_data)
            print(f"[cyan] Item registrado: {item_data.get('name')}[/cyan]")

'''
        
        if mod_data['features']['enemies']:
            content += '''def register_enemies(api, config):
    """Registra nuevos enemigos del mod"""
    
    enemies_config = config.get('enemies', {})
    
    for enemy_id, enemy_data in enemies_config.items():
        api.register_enemy(cEnemy, enemy_data)
        print(f"[red] Enemigo registrado: {enemy_data.get('NAME')}[/red]")

'''
        
        if mod_data['features']['zones']:
            content += '''def register_zones(api, config):
    """Registra nuevas zonas del mod"""
    
    zones_config = config.get('zones', {})
    
    for zone_name, zone_data in zones_config.items():
        api.register_zone(zone_name, zone_data)
        print(f"[blue] Zona registrada: {zone_name}[/blue]")

'''
        
        if mod_data['features']['events']:
            content += '''def register_events(api):
    """Registra manejadores de eventos"""
    
    def on_player_level_up(player):
        print(f"[yellow] ¡{player.name} subió de nivel con {get_mod_info()['name']}![/yellow]")
    
    def on_enemy_defeated(player, enemy):
        print(f"[green] {enemy.NAME} derrotado! (Evento de {get_mod_info()['name']})[/green]")
    
    api.register_event_handler('player_level_up', on_player_level_up)
    api.register_event_handler('enemy_defeated', on_enemy_defeated)

'''
        
        if mod_data['features']['commands']:
            content += '''def register_commands(api):
    """Registra comandos personalizados"""
    
    def custom_command(player):
        """Comando de ejemplo"""
        print(f"[magenta] ¡Comando personalizado de {get_mod_info()['name']}![/magenta]")
        # Aquí puedes añadir la lógica de tu comando
        return True
    
    api.register_command('mi_comando', custom_command, 
                        f"Comando personalizado de {get_mod_info()['name']}")

'''
        
        content += '''def cleanup_mod():
    """Se llama cuando el mod se descarga"""
    print(f"[yellow] Limpiando recursos de {get_mod_info()['name']}...[/yellow]")
'''
        
        return content
    
    def _generate_config_json(self, mod_data):
        """Genera la configuración JSON del mod"""
        config = {}
        
        if mod_data['features']['items']:
            config['items'] = {
                'example_sword': {
                    'id': 1001,
                    'type': 'weapon',
                    'name': f'Espada de {mod_data["author"]}',
                    'physical_dmg_min': 15,
                    'physical_dmg_max': 25,
                    'magical_dmg_min': 5,
                    'magical_dmg_max': 10,
                    'gold_cost': 120,
                    'description': f'Una poderosa espada creada por {mod_data["author"]}'
                }
            }
        
        if mod_data['features']['enemies']:
            config['enemies'] = {
                'custom_beast': {
                    'id': f'{mod_data["mod_id"]}_beast',
                    'NAME': f'NPC {mod_data["author"]}',
                    'HP_M': 80,
                    'PHYSICAL_DMG': 25,
                    'MAGICAL_DMG': 15,
                    'PHYSICAL_DMG_min': 15,
                    'MAGICAL_DMG_min': 5,
                    'MP_M': 50,
                    'EXP_TO_PLAYER': 75,
                    'DEF': 10,
                    'LS': 2,
                    'DBUFF_TO_PLAYER': [],
                    'BUFF_RECEIVED': [],
                    'GOLD': 100,
                    'zone': 'custom_zone'
                }
            }
        
        if mod_data['features']['zones']:
            config['zones'] = {
                f'{mod_data["mod_id"]}_zone': {
                    'name': f'Zona de {mod_data["author"]}',
                    'description': f'Una misteriosa zona creada por {mod_data["author"]}',
                    'enemies': ['custom_beast'],
                    'level_requirement': 5
                }
            }
        
        return config
    
    def _generate_readme(self, mod_data):
        """Genera el README.md del mod"""
        return f'''# {mod_data['name']}

**Versión:** {mod_data['version']}  
**Autor:** {mod_data['author']}

{mod_data['description']}

## Características

'''+ ('-  Nuevos items y armas\n' if mod_data['features']['items'] else '') + \
('-  Nuevos enemigos\n' if mod_data['features']['enemies'] else '') + \
('-  Nuevas zonas\n' if mod_data['features']['zones'] else '') + \
('-  Comandos personalizados\n' if mod_data['features']['commands'] else '') + \
('-  Manejadores de eventos\n' if mod_data['features']['events'] else '') + f'''

## Instalación

1. Copia la carpeta `{mod_data['mod_id']}` al directorio `mods/` del juego
2. Reinicia el juego
3. El mod se cargará automáticamente

## Configuración

Puedes modificar el archivo `config/config.json` para personalizar:

''' + ('- Estadísticas de armas y items\n' if mod_data['features']['items'] else '') + \
('- Estadísticas de enemigos\n' if mod_data['features']['enemies'] else '') + \
('- Configuración de zonas\n' if mod_data['features']['zones'] else '') + f'''

## Desarrollo

Para modificar este mod:

1. Edita `main.py` para la lógica principal
2. Modifica `config/config.json` para cambiar valores
3. Actualiza este README con tus cambios

## Licencia

Desarrollado para TPPRPG por {mod_data['author']}.
'''
    
    def list_mods(self):
        """Lista todos los mods disponibles"""
        if not self.mods_directory.exists():
            console.print("[yellow]No hay mods instalados[/yellow]")
            return
        
        mods = []
        for mod_dir in self.mods_directory.iterdir():
            if mod_dir.is_dir() and (mod_dir / "mod.json").exists():
                try:
                    with open(mod_dir / "mod.json", 'r', encoding='utf-8') as f:
                        mod_info = json.load(f)
                    mods.append((mod_dir.name, mod_info))
                except:
                    mods.append((mod_dir.name, {"name": mod_dir.name, "version": "?", "author": "?"}))
        
        if not mods:
            console.print("[yellow]No se encontraron mods válidos[/yellow]")
            return
        
        table = Table(title="Mods Instalados")
        table.add_column("ID", style="cyan")
        table.add_column("Nombre", style="green")
        table.add_column("Versión", style="magenta")
        table.add_column("Autor", style="yellow")
        
        for mod_id, mod_info in mods:
            table.add_row(
                mod_id,
                mod_info.get('name', mod_id),
                mod_info.get('version', '?'),
                mod_info.get('author', '?')
            )
        
        console.print(table)
    
    def validate_mod(self, mod_id):
        """Valida la estructura de un mod"""
        mod_dir = self.mods_directory / mod_id
        
        if not mod_dir.exists():
            console.print(f"[red]✗ Mod '{mod_id}' no encontrado[/red]")
            return False
        
        console.print(f"[cyan]Validando mod: {mod_id}[/cyan]")
        issues = []
        
        # Verificar mod.json
        mod_json = mod_dir / "mod.json"
        if not mod_json.exists():
            issues.append(" Falta mod.json")
        else:
            try:
                with open(mod_json, 'r', encoding='utf-8') as f:
                    json.load(f)
                console.print(" mod.json válido")
            except:
                issues.append(" mod.json malformado")
        
        # Verificar main.py
        main_py = mod_dir / "main.py"
        if not main_py.exists():
            issues.append(" Falta main.py")
        else:
            console.print(" main.py encontrado")
        
        # Verificar función init_mod
        if main_py.exists():
            try:
                with open(main_py, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'def init_mod(' in content:
                    console.print(" Función init_mod encontrada")
                else:
                    issues.append("  Función init_mod no encontrada")
            except:
                issues.append(" No se puede leer main.py")
        
        if issues:
            console.print("[yellow]Problemas encontrados:[/yellow]")
            for issue in issues:
                console.print(f"  {issue}")
            return False
        else:
            console.print("[green] Mod válido![/green]")
            return True

def main_dev_menu():
    """Menú principal de herramientas de desarrollo"""
    dev_kit = ModDevKit()
    
    while True:
        console.print(Panel(" Kit de Desarrollo de Mods TPPRPG", style="cyan"))
        console.print("1.  Crear nuevo mod")
        console.print("2.  Listar mods instalados")
        console.print("3.  Validar mod")
        console.print("4.  Documentación API")
        console.print("0.  Salir")
        
        choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4"])
        
        if choice == "0":
            break
        elif choice == "1":
            dev_kit.create_new_mod()
        elif choice == "2":
            dev_kit.list_mods()
        elif choice == "3":
            mod_id = Prompt.ask("ID del mod a validar")
            dev_kit.validate_mod(mod_id)
        elif choice == "4":
            show_api_documentation()
        
        if choice != "0":
            Prompt.ask("\nPresiona Enter para continuar")

def show_api_documentation():
    """Muestra la documentación de la API de mods"""
    console.print(Panel("📚 Documentación API de Mods", style="green"))
    
    doc_content = """
[bold cyan]Funciones principales del mod:[/bold cyan]

• [yellow]init_mod(api)[/yellow] - Función principal llamada al cargar el mod
• [yellow]cleanup_mod()[/yellow] - Función opcional llamada al descargar el mod
• [yellow]get_mod_info()[/yellow] - Retorna información del mod

[bold cyan]API disponible:[/bold cyan]

• [green]api.register_item(item_class, item_data)[/green]
  Registra nuevos items/armas/equipamiento
  
• [green]api.register_enemy(enemy_class, enemy_data)[/green]
  Registra nuevos enemigos
  
• [green]api.register_zone(zone_name, zone_data)[/green]
  Registra nuevas zonas/áreas
  
• [green]api.register_event_handler(event_name, handler_func)[/green]
  Registra manejadores de eventos del juego
  
• [green]api.register_command(command_name, handler_func, description)[/green]
  Añade comandos personalizados
  
• [green]api.register_shop(shop_name, shop_data)[/green]
  Registra nuevas tiendas

[bold cyan]Eventos disponibles:[/bold cyan]

• [magenta]player_level_up[/magenta] - Cuando el jugador sube de nivel
• [magenta]enemy_defeated[/magenta] - Cuando se derrota un enemigo
• [magenta]item_equipped[/magenta] - Cuando se equipa un item
• [magenta]combat_start[/magenta] - Al iniciar combate
• [magenta]combat_end[/magenta] - Al terminar combate

[bold cyan]Clases disponibles:[/bold cyan]

• [blue]cWeapon[/blue] - Para crear armas
• [blue]cEquippableItems[/blue] - Para crear equipamiento
• [blue]cObject[/blue] - Para crear objetos usables
• [blue]cEnemy[/blue] - Para crear enemigos
"""
    
    console.print(doc_content)

if __name__ == "__main__":
    main_dev_menu()
