"""
4 v0
Creado por: 423

4
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
        print(f"Error cargando configuración: {e}")
    return {}

def init_mod(api):
    """
    Función principal que se llama cuando el mod se carga
    """
    print(f"[green]🚀 Cargando 4 v0[/green]")
    
    config = load_config()
    
    # Registrar nuevos items
    register_items(api, config)
    
    # Registrar nuevos enemigos
    register_enemies(api, config)
    
    # Registrar nuevas zonas
    register_zones(api, config)
    
    # Registrar manejadores de eventos
    register_events(api)
    
    # Registrar comandos personalizados
    register_commands(api)
    
    print(f"[green]✅ {get_mod_info()['name']} cargado exitosamente![/green]")

def get_mod_info():
    """Información del mod"""
    return {
        "name": "4",
        "version": "0",
        "author": "423"
    }

def register_items(api, config):
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
            print(f"[cyan]🗡️ Item registrado: {item_data.get('name')}[/cyan]")

def register_enemies(api, config):
    """Registra nuevos enemigos del mod"""
    
    enemies_config = config.get('enemies', {})
    
    for enemy_id, enemy_data in enemies_config.items():
        api.register_enemy(cEnemy, enemy_data)
        print(f"[red]👹 Enemigo registrado: {enemy_data.get('NAME')}[/red]")

def register_zones(api, config):
    """Registra nuevas zonas del mod"""
    
    zones_config = config.get('zones', {})
    
    for zone_name, zone_data in zones_config.items():
        api.register_zone(zone_name, zone_data)
        print(f"[blue]🗺️ Zona registrada: {zone_name}[/blue]")

def register_events(api):
    """Registra manejadores de eventos"""
    
    def on_player_level_up(player):
        print(f"[yellow]🎉 ¡{player.name} subió de nivel con {get_mod_info()['name']}![/yellow]")
    
    def on_enemy_defeated(player, enemy):
        print(f"[green]⚔️ {enemy.NAME} derrotado! (Evento de {get_mod_info()['name']})[/green]")
    
    api.register_event_handler('player_level_up', on_player_level_up)
    api.register_event_handler('enemy_defeated', on_enemy_defeated)

def register_commands(api):
    """Registra comandos personalizados"""
    
    def custom_command(player):
        """Comando de ejemplo"""
        print(f"[magenta]✨ ¡Comando personalizado de {get_mod_info()['name']}![/magenta]")
        # Aquí puedes añadir la lógica de tu comando
        return True
    
    api.register_command('mi_comando', custom_command, 
                        f"Comando personalizado de {get_mod_info()['name']}")

def cleanup_mod():
    """Se llama cuando el mod se descarga"""
    print(f"[yellow]🧹 Limpiando recursos de {get_mod_info()['name']}...[/yellow]")
