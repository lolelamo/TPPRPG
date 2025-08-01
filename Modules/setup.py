from rich.console import Console
from rich.theme import Theme
from Modules.Loader import Write, Read

import random
import time as sp
import keyboard

##################      First Variables
player = None
LObject = []
console = Console()

##################      Classes
class cPlayer:
    """ 
    Player class
    
    Status:
        Health & Health_max
        Mana & Mana_max
        EXP: Current XP
        EXP_M: EXP needed for next level
        Gold: Current money
        Level: +1 when EXP >= EXP_M, 1+ skill point and 5+ Health_max
    
    Attributes:
        DEF: (DEF * 0.7) - Damage, Ignores Debuff Damage
        MDEF: (MDEF * 0.5) - Magical Damage, Debuff Damage counts as Magical Damage
        AGI: AGI% of Dealing damage (base 60%)
        DefensePercentage: Blocks a percentaje of the incoming damage, Ignores Debuff Damage
        CounterAttack: CounterAttack% of attack without using a turn when you receive damage from a enemy, Ignores Debuff Damage
        ManaRegen: Every Turn you regen mana based on this variable value: Mana+= ManaRegen
        EvadeAttacks: EvadeAttacks% of not receiving incoming Damage
        
    Items:
        Helmet: 

        """
        
    
    def __init__(self, name, weapon):
        self.name = name
        # Main Stats
        self.Health_max = 100
        self.Health = self.Health_max
        self.Mana_max = 100
        self.Mana = self.Mana_max
        self.Level = 1
        # Secondary Stats
        self.DEF = 0
        self.MDEF = 0
        self.AGI = 0
        self.DefensePercentage = 0
        self.CounterAttack = 0
        self.EvadeAttacks = 0
        self.ManaRegen = 2.5
        # Gold and Experience
        self.Gold = 50
        self.EXP = 0
        self.EXP_M = 100
        # Items
        self.weapon = weapon
        self.helmet = None
        self.armor = cEquippableItems(2, "Armadura", 5, 0, 0, 0, 20, "...", "Armor")
        self.boots = None
        self.ring = None
        self.ring2 = None
        self.ring3 = None
        self.items_in_PlayerClass = [self.weapon, self.helmet, self.armor, self.boots, self.ring, self.ring2, self.ring3]
        self.applieddebuffs = []
        self.appliedbuffs = []
        self.companion = []
        self.lobjectscheck = [
            (self.helmet, "Helmet"),
            (self.armor, "Armor"),
            (self.boots, "Boots"),
            (self.ring, "Ring"),
            (self.ring2, "Ring"),
            (self.ring3, "Ring")
        ]
    # TODO: instead of checking if the weapon has atleast 0.1 dmg
    # it should check if the player has a weapon and use its stats
    # if its None then it should use a default weapon

    def attack(self, enemy):
        """ Attack an enemy with physical and magical damage """
        damage = 0
        physical_damage = 0
        magical_damage = 0
        
        if self.weapon is not None:
            # Get physical and magical damage from weapon
            physical_dmg, magical_dmg = self.weapon.use_weapon(self)
            
            # Apply defense calculations TODO: Formulas are wrong
            physical_damage = max(0, physical_dmg - (enemy.DEF // 2))
            magical_damage = max(0, magical_dmg - (enemy.MDEF // 1.2))
            
            # Total damage is the sum of both types
            damage = physical_damage + magical_damage
            
            if damage < 1:
                damage = 2
                physical_damage = 2
        else:
            # Base attack without weapon
            damage = random.randint(1, 3)
            physical_damage = damage
        
        # Apply damage to enemy
        enemy.TakeDamage(damage)
        
        # Display attack message
        print(f"{self.name} ataca a {enemy.NAME}", end=" ")
        
        if self.weapon is not None:
            if magical_damage > 0:
                print(f"con {self.weapon.name} causando {damage:.1f} de daño! (Físico: {physical_damage:.1f}, Mágico: {magical_damage:.1f})")
            else:
                print(f"con {self.weapon.name} causando {damage:.1f} de daño físico!")
        else:
            print(f"con sus puños causando {damage} de daño!")
        
        return damage

    def TakeDamage(self, damage):
        """ Reduces player's HP based on the {damage} variable, 
            it needs to be a float or int value"""
        self.Health -= damage
        if self.Health < 0:
            self.Health = 0

    def win(self, quantity, quantity2):
        """ This shall be called when the player defeats an enemy, 
        {quantity} is EXP 
        {quantity2}  is GOLD"""

        self.EXP += quantity
        self.Gold += quantity2
        if player.Level >= 2:
            player.EXP_M *= round(1.07)
        if self.EXP >= player.EXP_M:
            while self.EXP >= self.EXP_M:
                self.Level += 1
                self.EXP -= self.EXP_M
                self.Health_max += 10
                self.Health += round(self.Health_max/3.18*1.145)
                print(f"{self.name} sube de Level y ahora es Level {self.Level}!")

    def PlayerObjects(self):
        """ Prints atrributes of the player's equipment """

        for item in self.items_in_PlayerClass:
            if isinstance(item, cEquippableItems):
                print(f"{item.name}", end=" ")
                for attr_name in ["ID", "Defense", "HealthBoost", "HealthSteal", "DmgBoost", "Description"]:
                    attr_value = getattr(item, attr_name, None)
                    if attr_value is not None and (isinstance(attr_value, (int, float)) and attr_value > 0):
                        if attr_name == "Description":
                            print(f"-Description: {attr_value}\n")
                        else:
                            print(f"-{attr_name}: {attr_value}", end=" ")

                        
            elif isinstance(item, cWeapon):
                print(f"{item.name} -ID: {item.ID} -Daño {item.damage_min}/{item.damage_max} -Description: {item.Description}")
                print("\n")
    def Check(self, lInventory):
        """ {lInventory} """
        self.items_in_PlayerClass = [self.weapon, self.helmet, self.armor, self.boots, self.ring, self.ring2, self.ring3]
        Companion_Updater(self)
            
        if self.Health > self.Health_max:
            self.Health = self.Health_max
        if self.Mana > self.Mana_max:
            self.Mana = self.Mana_max

        for obj in self.items_in_PlayerClass:
            if isinstance(obj, cObject):
                setattr(self, "Object", None)
                lInventory.addObject(obj)
        if self.Health <= 0:
            self.Health = self.Health_max
            self.Gold -= (self.Health_max * 0.6)
        
        for item in self.items_in_PlayerClass:
            if isinstance(item, cEquippableItems) and item.AppliedStats == False:
                self.DEF += item.Defense
                self.Health_max += item.HealthBoost
                
        for item, objecttype in self.lobjectscheck:
            if item and objecttype is not None:
                if item.objectcheck != objecttype:
                    lInventory.append(item)
                    setattr(self, objecttype.lower(), None)
        

        
    def Equip(self, vInventory, InventorySortervar, player):
        print("\nInventario: \n")
        try:
            EquipInput = int(input("[1]- Equipa [2]-Desequipar"))
        except Exception as e:
            print(f"\nException\n{e}") # Necesita revision 08/02/2024
        if EquipInput == 1:
            for i, var in enumerate(vInventory.lObjectsInventory, start=1):
                if var is not None:
                    if i % 2 == 0:
                        print(f"ID: {var.ID} | {var.name}\t", end=" ")
                    else:
                        print(f"ID: {var.ID} | {var.name}\t", end="\n")
            print("\nIngresa el ID del Objeto: \n")
        elif EquipInput == 2:
            for i, var in enumerate(vInventory.lObjectsInventory, start=1):
                if var is not None:
                    if i % 2 == 0:
                        print(f"ID: {var.ID} | {var.name}\t", end=" ")
                    else:
                        print(f"ID: {var.ID} | {var.name}\t", end="\n")
            print("\nIngresa el ID del Objeto: \n")

            EquipInput = int(input("ID:: "))
            weapon_get = InventorySortervar.SearchObject(EquipInput)
            print(weapon_get.name)

            if isinstance(weapon_get, cEquippableItems):
                if weapon_get.objectcheck == "Ring" or weapon_get.objectcheck == "ring":
                    for ring in [self.ring, self.ring2, self.ring3]:
                        if ring is None:
                            ring = InventorySortervar
                            break
                        elif ring is not None:
                            vInventory.addObject(ring)
                            ring = InventorySortervar
                            break
                else:
                    setattr(self, weapon_get.objectcheck.lower(), InventorySortervar)

            elif isinstance(weapon_get, cWeapon):
                if self.weapon is not None:
                    vInventory.addObject(self.weapon)
                    print(f"Se desequipó {self.weapon.name}")

                player.weapon = weapon_get
                
                print(f"Se equipó {weapon_get.name}")
                vInventory.addObject(weapon_get, False)
                sp.sleep(3.5)

class cEnemy:
    def __init__ (self, NAME, 
                  HP_M,  
                  PHYSICAL_DMG, MAGICAL_DMG, 
                  PHYSICAL_DMG_min, MAGICAL_DMG_min, 
                  MP_M, 
                  EXP_TO_PLAYER, 
                  DEF, LS, 
                  DBUFF_TO_PLAYER, 
                  BUFF_RECEIVED,
                  GOLD):
        self.NAME = NAME
        self.HP_M = HP_M
        self.HP = self.HP_M
        self.PHYSICAL_DMG = PHYSICAL_DMG
        self.MAGICAL_DMG = MAGICAL_DMG
        self.PHYSICAL_DMG_min = PHYSICAL_DMG_min
        self.MAGICAL_DMG_min = MAGICAL_DMG_min
        self.MP_M = MP_M
        self.MP = self.MP_M
        self.EXP_TO_PLAYER = EXP_TO_PLAYER
        self.DEF = DEF
        self.LS = LS
        self.DBUFF_TO_PLAYER = DBUFF_TO_PLAYER
        self.BUFF_RECEIVED = BUFF_RECEIVED
        self.GOLD = GOLD

    def attack(self, player):
        """Attack player with physical and magical damage"""
        # Calculate physical damage
        physical_damage = max(0, random.randint(self.PHYSICAL_DMG_min, self.PHYSICAL_DMG) - (player.DEF / 2))
        
        # Calculate magical damage
        magical_damage = max(0, random.randint(self.MAGICAL_DMG_min, self.MAGICAL_DMG) - (player.MDEF / 1.6))
        
        # Total damage is the sum of both types
        total_damage = physical_damage + magical_damage
        
        # Apply damage to player
        player.TakeDamage(total_damage)
        
        # Display damage breakdown
        if magical_damage > 0:
            print(f"\n{self.NAME} ataca a {player.name} causando {total_damage:.1f} puntos de daño! (Físico: {physical_damage:.1f}, Mágico: {magical_damage:.1f})")
        else:
            print(f"\n{self.NAME} ataca a {player.name} causando {total_damage:.1f} puntos de daño físico!")
        
        return total_damage

    def TakeDamage(self, damage):
        self.HP -= damage 
        if self.HP < 0:
            self.HP = 0
    


class cWeapon:
    def __init__(self, ID, name, physical_dmg_min, physical_dmg_max, magical_dmg_min, magical_dmg_max, Gold_Cost, Description):
        self.ID = ID
        self.name = name
        self.PHYSICAL_DMG = physical_dmg_max
        self.PHYSICAL_DMG_min = physical_dmg_min
        self.MAGICAL_DMG = magical_dmg_max
        self.MAGICAL_DMG_min = magical_dmg_min
        # For backward compatibility
        self.damage_min = physical_dmg_min
        self.damage_max = physical_dmg_max
        self.Gold_Cost = Gold_Cost
        self.Description = Description
        self.AppliedStats = False
        LObject.append(self)
        

    def use_weapon(self, player=None):
        if player is None or player.weapon is None:
            return (random.randint(2, 5), 0)  # Base physical damage, no magical
        
        physical = random.randint(self.PHYSICAL_DMG_min, self.PHYSICAL_DMG)
        magical = random.randint(self.MAGICAL_DMG_min, self.MAGICAL_DMG)
        
        # Apply boosts from equipment
        for item in [player.ring, player.ring2, player.ring3, player.armor]:
            if item and hasattr(item, 'DmgBoost'):
                physical += item.DmgBoost
        
        return (physical, magical)
    
class cEquippableItems:
    def __init__(self, ID, name, Defense, HealthBoost, HealthSteal, DmgBoost, Gold_Cost, Description, objectcheck):
        self.ID = ID
        self.name = name
        self.Defense = Defense
        self.HealthBoost = HealthBoost
        self.HealthSteal = HealthSteal
        self.DmgBoost = DmgBoost
        self.Gold_Cost = Gold_Cost
        self.Description = Description
        self.objectcheck = objectcheck
        self.AppliedStats = False

        LObject.append(self)
        


class cObject:
    def __init__(self, ID, name, Health, Defense, Gold_Cost, Description):
        self.ID = ID
        self.name = name
        self.Health = Health
        self.Defense = Defense
        self.Gold_Cost = Gold_Cost
        self.Description = Description
        LObject.append(self)
        

class cInventory:
    def __init__(self):
        self.lObjectsInventory = []
        self.lObjectsInventory = sorted(self.lObjectsInventory, key=lambda x: x.ID)

    def addObject(self, vObject, appenditem=True):
        if appenditem:
            self.lObjectsInventory.append(vObject)
        elif appenditem == False:
            self.lObjectsInventory.remove(vObject)


    def PrintObjects(self):
        print("\nInventario: \n")
        for vObject in self.lObjectsInventory:
            if isinstance(vObject, cWeapon):
                print(f"--{vObject.name} - Daño: {vObject.damage_min}/{vObject.damage_max} - Description: {vObject.Description}")
            elif isinstance(vObject, cEquippableItems):
                print(f"--{vObject.name}", end=" ")
                for attr_name in ["Defense", "HealthBoost", "HealthSteal", "DmgBoost", "Description"]:
                    attr_value = getattr(vObject, attr_name, None)
                    if attr_value is not None and (isinstance(attr_value, (int, float)) and attr_value > 0):
                        if attr_name == "Description":
                            print(f"- Description: {attr_value}", end=" ")
                        else:
                            print(f"- {attr_name}: {attr_value}", end=" ")
                print("\n")               
            elif isinstance(vObject, cObject):
                print(f"{vObject.name}", end=" ")
                for attr_name in []:
                    attr_value = getattr(vObject, attr_name, None)
                    if attr_value is not None and (isinstance(attr_value, (int, float)) and attr_value > 0):
                        if attr_name == "Description":
                            print(f"-Description: {attr_value}", end=" ")
                        else:
                            print(f"- {attr_name}: {attr_value}", end=" ")
                print("\n")
            else:
                print("[yellow]No hay objetos en el inventario[/yellow]")
        print("\nPresiona enter ↵")
        keyboard.wait("enter", suppress=True)

    
class cDebuff:
    def __init__(self, name, PersistentDamageDebuff=None, HealDebuff=None, ArmorPierce=None, AgilityDebuff=None, MPDisruption=None, EvadeDebuff=None, CounterAttackDebuff=None): 
        self.name = name
        self.PersistentDamageDebuff = PersistentDamageDebuff
        self.HealDebuff = HealDebuff
        self.ArmorPierce = ArmorPierce
        self.AgilityDebuff = AgilityDebuff
        self.MPDisruption = MPDisruption
        self.EvadeDebuff = EvadeDebuff
        self.CounterAttackDebuff = CounterAttackDebuff

    def Apply(self, Value, player):
        if Value is not None:
            if hasattr(self, Value):
                debuff_value = getattr(self, Value, None)
                if debuff_value is not None:
                    if Value == "PersistentDamageDebuff":
                        NotImplemented
                    if Value == "HealDebuff":
                        player.Health -= debuff_value
                    if Value == "ArmorPierce":
                        player.Defense -= debuff_value
                    if Value == "AgilityDebuff":
                        NotImplemented
                    if Value == "MPDisruption":
                        NotImplemented                    
                    if Value == "EvadeDebuff":
                        NotImplemented
                    if Value == "CounterAttackDebuff":
                        NotImplemented

class cBuffs:
    def __init__(self, name, EvadeBuff=None, Heal=None, MagicArmor=None, MPregen=None, Strenght=None):    
        self.name = name
        self.EvadeBuff = EvadeBuff
        self.Heal = Heal
        self.MagicArmor = MagicArmor
        self.MPregen = MPregen
        self.Strength = Strenght

class cIDSorter:
    def __init__(self, lvObjects):
        self.lvObjects = lvObjects

    def SearchObject(self, ID):
        for vObject in self.lvObjects:
            if vObject.ID == ID:
                return vObject
        
class cShop:
    def __init__(self, BuyObject, Gold_Cost):
        self.BuyObject = BuyObject
        self.Gold_Cost = Gold_Cost

    def buy(self):
        if player.Gold >= self.Gold_Cost:
            player.Gold -= self.Gold_Cost
            vInventory.addObject(self.BuyObject)
            print(f"Se ha comprado: {self.BuyObject.name}")
        else:
            text_input = "No tienes Dinero suficiente"
            print(f"Dinero actual: {player.Gold}")
            print(f"El vObject cuesta: {self.Gold_Cost}")
            return text_input

##################      Variables
vInventory = cInventory()
InventorySorter = cIDSorter(vInventory.lObjectsInventory)
LObjectSorter = cIDSorter(LObject)
SLObject = sorted(LObject, key=lambda x: x.ID)

##################      Defs
def setup_player():
    try:
        NamePlayer = input("N:: ") 
    except Exception as e:
        NameLoop = True
        print(f"Error descnonocido\n Exception:\n{e}")
        while NameLoop == True:
                try:
                    NamePlayer = input("\nN:: ")
                    NameLoop = False
                except Exception as e:
                    Write("\\logs\\logs.txt", None, None, "[Crit]", e, True, True)
        del NameLoop
    return(cPlayer(NamePlayer, None))

def fShop(player):
    try:
        if text_input is not None:
            pass
    except:
        Write("\\")
        text_input = None

    LoopShopEvent = True
    player.Check(vInventory)
    i += 0
    while LoopShopEvent:
        for ItemShop in SLObject:
            print(f"Objeto: {ItemShop.name} --Coste: {ItemShop.Gold_Cost}")
            i += 1
            if i == 5:
                break
        if text_input is not None:
            SInputShop = input(text_input)
            SInputShop = int(SInputShop)
        elif text_input is None:
            SInputShop = input("ID::")
            SInputShop = int(SInputShop)
        for Item in SLObject:
            if Item.ID == SInputShop:

                LOBject_item = LObjectSorter.SearchObject(SInputShop)

                if LOBject_item is not None:
                    print(f"\nQuieres comprar {LOBject_item.name}?")
                    print(f"Dinero Actual: {player.Gold}")
                    v = input("Y/N:: ")
                    if v.lower() == "y":
                        varShopHandler = cShop(LOBject_item, LOBject_item.Gold_Cost)
                        varShopHandler.buy()

                    elif v.lower() == "n":
                        LoopShopEvent = False  

                elif Item is None:
                    text_input = "No se ha encontrado el objeto. ID:: "
                    #keyboard.wait("Presiona enter...")
        else:
            text_input = "ID no encontrado. Introduce un ID válido. ID::"

def Companion_Updater(player):
    Chars = []
    for c in player.companion:
        Chars.append(c)

def enemy_loader(data_npc, return_single=False):
    """
    Load enemy data from JSON, properly handling physical and magical damage arrays.
    
    Args:
        data_npc: Enemy data from JSON
        return_single: If True, returns a single random enemy; if False, returns list
        
    Returns:
        List of enemy objects or single enemy object if return_single is True
    """
    enemy_total_list = []
    
    for enemy_group in data_npc:
        for key, enemy_data in enemy_group.items():
            if key != "Strings":
                try:
                    # Extract physical and magical damage with safe fallbacks
                    dmg_array = enemy_data.get('DMG', [0, 0])
                    dmg_min_array = enemy_data.get('DMG_min', [0, 0])
                    
                    # Ensure arrays have proper format
                    if not isinstance(dmg_array, list):
                        dmg_array = [dmg_array, 0]
                    if not isinstance(dmg_min_array, list):
                        dmg_min_array = [dmg_min_array, 0]
                    
                    # Extract individual values with safe indexing
                    physical_dmg = dmg_array[0] if len(dmg_array) > 0 else 0
                    magical_dmg = dmg_array[1] if len(dmg_array) > 1 else 0
                    physical_dmg_min = dmg_min_array[0] if len(dmg_min_array) > 0 else 0
                    magical_dmg_min = dmg_min_array[1] if len(dmg_min_array) > 1 else 0
                    
                    # Create enemy instance with separated damage types
                    enemy_load_var = cEnemy(
                        NAME=enemy_data.get('NAME', 'Unknown'),
                        HP_M=enemy_data.get('HP_M', 10),
                        PHYSICAL_DMG=physical_dmg,
                        MAGICAL_DMG=magical_dmg,
                        PHYSICAL_DMG_min=physical_dmg_min,
                        MAGICAL_DMG_min=magical_dmg_min,
                        MP_M=enemy_data.get('MP_M', 0),
                        EXP_TO_PLAYER=enemy_data.get('EXP_TO_PLAYER', 0),
                        DEF=enemy_data.get('DEF', 0),
                        LS=enemy_data.get('LS', 0),
                        DBUFF_TO_PLAYER=enemy_data.get('DBUFF_TO_PLAYER', []),
                        BUFF_RECEIVED=enemy_data.get('BUFF_RECEIVED', []),
                        GOLD=enemy_data.get('GOLD', 0)
                    )
                    enemy_total_list.append(enemy_load_var)
                except Exception as e:
                    print(f"Error loading enemy {key}: {str(e)}")
                    continue
    
    if not enemy_total_list:
        return [] if not return_single else None
        
    return enemy_total_list if not return_single else random.choice(enemy_total_list)
