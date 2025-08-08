"""
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
