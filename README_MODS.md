# 🛠️ Sistema de Mods para TPPRPG

Este README explica cómo usar y desarrollar mods para tu juego RPG de texto, similar al sistema de Minecraft Forge.

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Instalación y Uso](#instalación-y-uso)
3. [Desarrollo de Mods](#desarrollo-de-mods)
4. [API de Mods](#api-de-mods)
5. [Ejemplos](#ejemplos)
6. [Herramientas de Desarrollo](#herramientas-de-desarrollo)
7. [Estructura de Archivos](#estructura-de-archivos)


### Estructura

```
TPPRPG/
├── mods/
│   ├── example_mod/
│   │   ├── mod.json
│   │   ├── main.py
│   │   ├── config/
│   │   │   └── config.json
│   │   ├── assets/
│   │   └── README.md
│   └── otro_mod/
├── Modules/
├── Data/
└── MainGame.py
```

## Desarrollo de Mods

### Creación Automática

Usa las **Herramientas de Desarrollo** (opción 9 del menú):

```bash
python MainGame.py
# Selecciona opción 9: Herramientas de Desarrollo
# Selecciona opción 1: Crear nuevo mod
```

### Creación Manual

1. **Crear Directorio**: `mods/mi_mod/`
2. **Archivo mod.json**:

```json
{
    "mod_id": "mi_mod",
    "name": "Mi Increíble Mod",
    "version": "1.0.0",
    "author": "Tu Nombre",
    "description": "Un mod increíble para TPPRPG",
    "main": "main.py",
    "dependencies": [],
    "game_version": "1.0.0"
}
```

3. **Archivo main.py**:

```python
def init_mod(api):
    """Función principal del mod"""
    print(f"[green]Cargando Mi Increíble Mod v1.0.0[/green]")
    
    # Tu código aquí
    register_items(api)
    register_enemies(api)

def register_items(api):
    """Registrar nuevos items"""
    from Modules.setup import cWeapon
    
    # Crear espada personalizada
    espada_magica = cWeapon(
        ID=1001,
        name="Espada Mágica",
        physical_dmg_min=20,
        physical_dmg_max=35,
        magical_dmg_min=10,
        magical_dmg_max=20,
        Gold_Cost=150,
        Description="Una espada imbuida con poder elemental"
    )
    
    api.register_item(cWeapon, {
        'id': 'espada_magica',
        'name': 'Espada Mágica',
        'physical_dmg_min': 20,
        'physical_dmg_max': 35,
        'magical_dmg_min': 10,
        'magical_dmg_max': 20,
        'gold_cost': 150,
        'description': 'Una espada imbuida con poder elemental'
    })

def register_enemies(api):
    """Registrar nuevos enemigos"""
    from Modules.setup import cEnemy
    
    dragon_data = {
        'id': 'dragon_de_fuego',
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

def cleanup_mod():
    """Limpieza al descargar el mod (opcional)"""
    print("Limpiando Mi Increíble Mod...")
```

## 🔧 API de Mods

### Funciones Principales

| Función | Descripción |
|---------|-------------|
| `init_mod(api)` | **Obligatoria** - Se ejecuta al cargar el mod |
| `cleanup_mod()` | Opcional - Se ejecuta al descargar el mod |
| `get_mod_info()` | Opcional - Retorna información del mod |

### Métodos de la API

#### Registro de Contenido

```python
# Registrar items/armas/equipamiento
api.register_item(item_class, item_data)

# Registrar enemigos
api.register_enemy(enemy_class, enemy_data)

# Registrar zonas
api.register_zone(zone_name, zone_data)

# Registrar tiendas
api.register_shop(shop_name, shop_data)
```

#### Sistema de Eventos

```python
# Registrar manejador de eventos
api.register_event_handler(event_name, handler_function)

# Eventos disponibles:
# - 'player_level_up': Cuando el jugador sube de nivel
# - 'enemy_defeated': Cuando se derrota un enemigo
# - 'item_equipped': Cuando se equipa un item
# - 'combat_start': Al iniciar combate
# - 'combat_end': Al terminar combate

def on_level_up(player):
    print(f"¡{player.name} subió de nivel!")

api.register_event_handler('player_level_up', on_level_up)
```

#### Comandos Personalizados

```python
# Registrar comando personalizado
api.register_command(command_name, handler_function, description)

def curar_magico(player):
    player.Health = min(player.Health + 50, player.Health_max)
    print("[green]¡Magia curativa![/green]")
    return True

api.register_command('curar_magico', curar_magico, "Cura 50 puntos de vida")
```

### Clases Disponibles

```python
from Modules.setup import cWeapon, cEnemy, cEquippableItems, cObject

# Crear arma
arma = cWeapon(ID, nombre, dmg_fis_min, dmg_fis_max, dmg_mag_min, dmg_mag_max, costo, descripcion)

# Crear enemigo  
enemigo = cEnemy(nombre, vida_max, dmg_fis, dmg_mag, dmg_fis_min, dmg_mag_min, mana_max, exp, defensa, ls, debuffs, buffs, oro)

# Crear equipamiento
equipo = cEquippableItems(ID, nombre, defensa, vida_boost, robo_vida, boost_dmg, costo, descripcion, tipo)

# Crear objeto usable
objeto = cObject(ID, nombre, vida, defensa, costo, descripcion)
```

## 📝 Ejemplos

### Mod Simple: Espada Poderosa

```python
def init_mod(api):
    from Modules.setup import cWeapon
    
    espada_data = {
        'id': 'espada_definitiva',
        'name': 'Espada Definitiva',
        'physical_dmg_min': 50,
        'physical_dmg_max': 75,
        'magical_dmg_min': 0,
        'magical_dmg_max': 0,
        'gold_cost': 500,
        'description': 'La espada más poderosa jamás forjada'
    }
    
    api.register_item(cWeapon, espada_data)
```

### Mod con Eventos: Bonus de Experiencia

```python
def init_mod(api):
    def bonus_exp(player, enemy):
        if enemy.NAME == "Dragón":
            bonus = 25
            player.EXP += bonus
            print(f"[yellow]¡Bonus por derrotar un dragón: +{bonus} EXP![/yellow]")
    
    api.register_event_handler('enemy_defeated', bonus_exp)
```

### Mod Complejo: Nueva Zona

```python
def init_mod(api):
    # Registrar zona
    zona_data = {
        'name': 'Templo Maldito',
        'description': 'Un templo antiguo lleno de peligros',
        'enemies': ['esqueleto_guardian', 'lich'],
        'level_requirement': 10
    }
    api.register_zone('templo_maldito', zona_data)
    
    # Registrar enemigos de la zona
    esqueleto_data = {
        'id': 'esqueleto_guardian',
        'NAME': 'Esqueleto Guardián',
        'HP_M': 80,
        'PHYSICAL_DMG': 25,
        'MAGICAL_DMG': 0,
        'PHYSICAL_DMG_min': 15,
        'MAGICAL_DMG_min': 0,
        'MP_M': 0,
        'EXP_TO_PLAYER': 60,
        'DEF': 15,
        'LS': 0,
        'DBUFF_TO_PLAYER': [],
        'BUFF_RECEIVED': [],
        'GOLD': 75,
        'zone': 'templo_maldito'
    }
    api.register_enemy(cEnemy, esqueleto_data)
```

## 🛠️ Herramientas de Desarrollo

Accede desde el menú principal (opción 9):

### 🆕 Crear Nuevo Mod
- Wizard interactivo para generar la estructura del mod
- Plantillas personalizables según características deseadas
- Configuración automática de archivos

### 📋 Listar Mods
- Visualiza todos los mods instalados
- Información detallada de cada mod
- Estado de carga

### 🔍 Validar Mod
- Verifica la estructura del mod
- Detecta errores comunes
- Sugiere correcciones

### 📖 Documentación API
- Referencia completa de la API
- Ejemplos de uso
- Lista de eventos disponibles

## 📁 Estructura de Archivos

### Mod Básico
```
mi_mod/
├── mod.json          # Información del mod
├── main.py           # Código principal
└── README.md         # Documentación
```

### Mod Avanzado
```
mi_mod/
├── mod.json          # Información del mod
├── main.py           # Código principal
├── config/
│   └── config.json   # Configuración personalizable
├── assets/
│   ├── sounds/       # Sonidos (futuro)
│   └── images/       # Imágenes (futuro)
├── lang/
│   └── es.json       # Traducciones (futuro)
└── README.md         # Documentación
```

### Archivo de Configuración (config.json)

```json
{
    "items": {
        "mi_espada": {
            "id": 1001,
            "type": "weapon",
            "name": "Mi Espada Personalizada",
            "physical_dmg_min": 15,
            "physical_dmg_max": 25,
            "magical_dmg_min": 5,
            "magical_dmg_max": 10,
            "gold_cost": 120,
            "description": "Una espada única creada por mi mod"
        }
    },
    "enemies": {
        "mi_monstruo": {
            "id": "mi_monstruo",
            "NAME": "Monstruo Personalizado",
            "HP_M": 100,
            "PHYSICAL_DMG": 30,
            "MAGICAL_DMG": 0,
            "PHYSICAL_DMG_min": 20,
            "MAGICAL_DMG_min": 0,
            "MP_M": 0,
            "EXP_TO_PLAYER": 80,
            "DEF": 12,
            "LS": 0,
            "DBUFF_TO_PLAYER": [],
            "BUFF_RECEIVED": [],
            "GOLD": 90,
            "zone": "custom_zone"
        }
    },
    "settings": {
        "debug_mode": false,
        "custom_multiplier": 1.5
    }
}
```

## 🎯 Consejos para Desarrolladores

### Buenas Prácticas

1. **IDs Únicos**: Usa prefijos para evitar conflictos
   ```python
   ID = 1000 + mi_numero  # IDs de mods empiezan en 1000+
   ```

2. **Manejo de Errores**: Siempre incluye try/except
   ```python
   try:
       # Tu código
   except Exception as e:
       print(f"Error en mi mod: {e}")
   ```

3. **Configuración Externa**: Usa archivos JSON para valores modificables
   ```python
   def load_config():
       with open("config/config.json", 'r') as f:
           return json.load(f)
   ```

4. **Documentación**: Incluye README.md detallado

5. **Versionado**: Sigue [Semantic Versioning](https://semver.org/)

### Limitaciones Actuales

- Los mods se cargan al inicio del juego
- No hay sistema de dependencias automático
- No hay interfaz gráfica para configuración
- Los eventos son limitados

### Funcionalidades Futuras

- 🔄 Recarga de mods en tiempo real
- 🎨 Soporte para assets gráficos
- 🌐 Traducciones múltiples
- 📦 Gestor de paquetes automático
- 🔗 Sistema de dependencias avanzado

## 🐛 Depuración y Solución de Problemas

### Logs

Los logs se guardan en `tpprpg_mods.log`:

```bash
tail -f tpprpg_mods.log  # Ver logs en tiempo real
```

### Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `mod.json no encontrado` | Falta el archivo | Crear mod.json válido |
| `init_mod no encontrado` | Falta función principal | Añadir def init_mod(api) |
| `ID duplicado` | Conflicto de IDs | Usar IDs únicos 1000+ |
| `Módulo no se puede importar` | Error en imports | Verificar rutas de imports |

### Validación

```bash
# Ejecutar herramientas de desarrollo
python MainGame.py
# Opción 9 → Opción 3 → Introducir ID del mod
```

## 📞 Soporte

- 📝 Consulta este README
- 🔍 Usa las herramientas de validación
- 📋 Revisa el mod de ejemplo incluido
- 🐛 Verifica los logs de error

---

¡Diviértete creando mods increíbles para TPPRPG! 🎮✨

<citations>
<document>
<document_type>RULE</document_type>
<document_id>7VndWmOcz7sliPFXEAEEI3</document_id>
</document>
<document>
<document_type>RULE</document_type>
<document_id>wCczWzGIsuVlGTUTODuk2l</document_id>
</document>
<document>
<document_type>RULE</document_type>
<document_id>yGiHuYvPgfc6JpREARAQxu</document_id>
</document>
</citations>
