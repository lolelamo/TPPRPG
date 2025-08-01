import json
import os
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='tpprpg.log',
    filemode='a'
)
logger = logging.getLogger('TPPRPG.Loader')

console = Console()

def Read(FilePath, Object, Content=None, Values=None):
    """ 
    Read and process JSON data from game files.
    
    Args:
        FilePath (str): Path to the JSON file
        Object (str): Primary key/section to access in the JSON
        Content (str, optional): Secondary key or special command to access nested data
        Values (any, optional): Additional parameter for more complex queries
    
    Returns:
        The requested data structure or an empty list/dict if not found
    """
    try:
        # Ensure the filepath uses consistent separators
        FilePath = os.path.normpath(FilePath)
        
        # Extract filename from path for file type detection
        filename = os.path.basename(FilePath).lower()
        
        with open(FilePath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            # If Object is None, return the entire data
            if Object is None:
                return data
            
            # Check if the key exists in the JSON
            if Object in data:
                # Handle different JSON file types based on filename
                if "datastats.json" in filename:
                    return _handle_datastats(data, Object, Content)
                elif "weapons.json" in filename:
                    return _handle_weapons(data, Object, Content)
                elif "datashops.json" in filename:
                    return _handle_shops(data, Object, Content)
                elif "saveslots.json" in filename or "savegame.json" in filename:
                    return _handle_saves(data, Object, Content)
                else:
                    # Generic handling for other JSON files
                    return _handle_generic_json(data, Object, Content)
            else:
                console.print(f"[yellow]Warning:[/] {Object} not found in the JSON file: {FilePath}")
                logger.warning(f"Object {Object} not found in {FilePath}")
                return []  # Return an empty list for consistency
                
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/] File '{FilePath}' not found.")
        logger.error(f"File not found: {FilePath} - {str(e)}")
        return []  # Return an empty list if the file doesn't exist
        
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error:[/] Failed to decode JSON (Malformed JSON): {e}")
        logger.error(f"JSON decode error in {FilePath}: {str(e)}")
        return []  # Return an empty list if the JSON is malformed
        
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/] {str(e)}")
        logger.error(f"Unexpected error reading {FilePath}: {str(e)}", exc_info=True)
        return []  # Handle any other unexpected errors

def _handle_datastats(data, Object, Content):
    """
    Handle DataStats.json structure with zones and enemies.
    
    Args:
        data: The loaded JSON data
        Object: The zone name (e.g., "Forest", "Cave")
        Content: What content to extract ("Strings" or None for all enemies)
    
    Returns:
        Processed zone data
    """
    if Content is None:
        # Return all enemy data for the zone
        return data[Object]
    elif Content == "Strings":
        # Extract the Strings object from the zone's array
        if isinstance(data[Object], list) and len(data[Object]) > 0:
            for item in data[Object]:
                if "Strings" in item:
                    return item["Strings"]
            
            # If we get here, "Strings" wasn't found
            console.print(f"[yellow]Warning:[/] 'Strings' not found in {Object}")
            logger.warning(f"'Strings' not found in {Object}")
            return {}
        else:
            console.print(f"[yellow]Warning:[/] Invalid structure for {Object}")
            logger.warning(f"Invalid structure for {Object}")
            return {}
    else:
        # Looking for a specific enemy or other content
        if isinstance(data[Object], list):
            for item in data[Object]:
                for key in item.keys():
                    if key == Content:
                        # Ensure DMG and DMG_min are handled as [Physical, Magical]
                        enemy_data = item[key]
                        if "DMG" in enemy_data and not isinstance(enemy_data["DMG"], list):
                            enemy_data["DMG"] = [enemy_data["DMG"], 0]  # Default to 0 magical damage
                        if "DMG_min" in enemy_data and not isinstance(enemy_data["DMG_min"], list):
                            enemy_data["DMG_min"] = [enemy_data["DMG_min"], 0]  # Default to 0 magical damage
                        return enemy_data
            
            # If the specific enemy wasn't found
            console.print(f"[yellow]Warning:[/] '{Content}' not found in {Object}")
            logger.warning(f"'{Content}' not found in {Object}")
            return {}
        else:
            return data[Object]

def _handle_weapons(data, Object, Content):
    """
    Handle weapons.json structure with TYPE: prefixes.
    
    Args:
        data: The loaded JSON data
        Object: The weapon type (e.g., "TYPE:Swords")
        Content: Specific weapon or None for all weapons of that type
    
    Returns:
        Processed weapon data
    """
    # Handle "TYPE:" prefix if not already included
    if not Object.startswith("TYPE:") and f"TYPE:{Object}" in data:
        Object = f"TYPE:{Object}"
    
    if Content is None:
        # Return all weapons of the specified type
        return data[Object]
    else:
        # Return specific weapon data
        if Content in data[Object]:
            weapon_data = data[Object][Content]
            # Ensure DMG and DMG_min are handled as [Physical, Magical]
            if "DMG" in weapon_data and not isinstance(weapon_data["DMG"], list):
                weapon_data["DMG"] = [weapon_data["DMG"], 0]
            if "DMG_min" in weapon_data and not isinstance(weapon_data["DMG_min"], list):
                weapon_data["DMG_min"] = [weapon_data["DMG_min"], 0]
            return weapon_data
        else:
            console.print(f"[yellow]Warning:[/] Weapon '{Content}' not found in {Object}")
            logger.warning(f"Weapon '{Content}' not found in {Object}")
            return {}

def _handle_shops(data, Object, Content):
    """
    Handle DataShops.json structure with shop weapon IDs.
    
    Args:
        data: The loaded JSON data
        Object: The shop name (e.g., "ForestShop")
        Content: Specific content or None for all shop data
    
    Returns:
        Processed shop data
    """
    if Content is None:
        # Return all shop data
        return data[Object]
    elif Content == "IDs":
        # Return just the weapon IDs array
        if isinstance(data[Object], list) and len(data[Object]) > 0 and "IDs" in data[Object][0]:
            return data[Object][0]["IDs"]
        else:
            console.print(f"[yellow]Warning:[/] 'IDs' not found in {Object}")
            logger.warning(f"'IDs' not found in {Object}")
            return []
    else:
        # Return specific shop data
        for item in data[Object]:
            if Content in item:
                return item[Content]
        
        console.print(f"[yellow]Warning:[/] '{Content}' not found in {Object}")
        logger.warning(f"'{Content}' not found in {Object}")
        return {}

def _handle_saves(data, SaveSlot, Content):
    """
    Handle SaveSlots.json structure with null values.
    
    Args:
        data: The loaded JSON data
        SaveSlot: The save slot (e.g., "Save1")
        Content: Specific content or None for all save data
    
    Returns:
        Processed save data
    """
    if Content is None:
        # Return all save data for the slot
        return data[SaveSlot]
    else:
        # Return specific save data, preserving null values
        save_data = data[SaveSlot].get(Content)
        return save_data  # This could be null/None, which is intentional

def _handle_generic_json(data, Object, Content):
    """
    Generic handler for other JSON files.
    
    Args:
        data: The loaded JSON data
        Object: The primary key
        Content: Secondary key or None
    
    Returns:
        Processed data
    """
    if Content is None:
        return data[Object]
    elif Content in data[Object]:
        return data[Object][Content]
    else:
        # Try to handle nested lists
        if isinstance(data[Object], list):
            for item in data[Object]:
                if isinstance(item, dict) and Content in item:
                    return item[Content]
            
            console.print(f"[yellow]Warning:[/] '{Content}' not found in {Object}")
            logger.warning(f"'{Content}' not found in {Object}")
            return {}
        else:
            console.print(f"[yellow]Warning:[/] '{Content}' not found in {Object}")
            logger.warning(f"'{Content}' not found in {Object}")
            return {}
    
def Write(FilePath, Object=None, Content=None, ToWrite=None, isplaintext=False):
    """ 
    Write data to JSON files or plain text files.
    
    Args:
        FilePath (str): Path to the file to write to
        Object (str, optional): Primary key/section to write in the JSON
        Content (str, optional): Secondary key or plain text content
        ToWrite (any, optional): Data to write (for JSON)
        isplaintext (bool): Whether to write as plain text (True) or JSON (False)
    """
    try:
        # Ensure the filepath uses consistent separators
        FilePath = os.path.normpath(FilePath)
        
        if isplaintext:
            # Create directory if it doesn't exist
            directory = Path(FilePath).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            # Append content to the file
            with open(FilePath, 'a', encoding='utf-8') as file:
                file.write(str(Content) + "\n")
            
            logger.info(f"Successfully wrote plain text to {FilePath}")
        else:
            # Extract filename from path for file type detection
            filename = os.path.basename(FilePath).lower()
            
            # Handle JSON writing
            try:
                # Create directory if it doesn't exist
                directory = Path(FilePath).parent
                directory.mkdir(parents=True, exist_ok=True)
                
                # Try to read existing data or create new data structure
                try:
                    with open(FilePath, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError):
                    data = {}

            except Exception as e:
                console.print(f"[yellow]Warning:[/] Failed to read existing file: {e}")
                logger.warning(f"Failed to read existing file {FilePath}: {str(e)}")
                data = {}

            # Determine the proper structure based on file type
            if Object:
                # Special handling for different file types
                if "datastats.json" in filename:
                    _write_datastats(data, Object, Content, ToWrite)
                elif "weapons.json" in filename:
                    _write_weapons(data, Object, Content, ToWrite)
                elif "datashops.json" in filename:
                    _write_shops(data, Object, Content, ToWrite)
                elif "saveslots.json" in filename or "savegame.json" in filename:
                    _write_saves(data, Object, Content, ToWrite)
                else:
                    # Default handling for generic JSON
                    _write_generic_json(data, Object, Content, ToWrite)
            
            # Write the updated data back to the file
            with open(FilePath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            
            logger.info(f"Successfully wrote JSON data to {FilePath}")
            
    except Exception as e:
        console.print(f"[bold red]Error writing to file:[/] {str(e)}")
        logger.error(f"Error writing to {FilePath}: {str(e)}", exc_info=True)

def _write_datastats(data, Object, Content, ToWrite):
    """
    Handle writing to DataStats.json with proper structure.
    
    Args:
        data: The existing JSON data
        Object: The zone name (e.g., "Forest", "Cave")
        Content: What content to write ("Strings" or enemy name)
        ToWrite: The data to write
    """
    # Ensure the zone exists as a list
    if Object not in data:
        data[Object] = [{}]
    elif not isinstance(data[Object], list):
        data[Object] = [data[Object]]
    
    if Content == "Strings":
        # Update or add Strings to the first item
        if len(data[Object]) == 0:
            data[Object].append({"Strings": ToWrite})
        else:
            data[Object][0]["Strings"] = ToWrite
    elif Content is not None:
        # Handle writing enemy data
        found = False
        for item in data[Object]:
            if Content in item:
                item[Content] = ToWrite
                found = True
                break
        
        if not found:
            # Add new enemy to the first dictionary in the list
            if len(data[Object]) > 0:
                data[Object][0][Content] = ToWrite
            else:
                data[Object].append({Content: ToWrite})
    else:
        # Overwrite the entire zone
        data[Object] = ToWrite

def _write_weapons(data, Object, Content, ToWrite):
    """
    Handle writing to weapons.json with TYPE: prefixes.
    
    Args:
        data: The existing JSON data
        Object: The weapon type (e.g., "TYPE:Swords" or "Swords")
        Content: Specific weapon name or None
        ToWrite: The data to write
    """
    # Handle "TYPE:" prefix if not already included
    if not Object.startswith("TYPE:") and not Object.startswith("TYPE:"):
        full_object = f"TYPE:{Object}"
    else:
        full_object = Object
    
    # Ensure the weapon type exists
    if full_object not in data:
        data[full_object] = {}
    
    if Content is not None:
        # Write specific weapon data
        data[full_object][Content] = ToWrite
    else:
        # Overwrite the entire weapon type
        data[full_object] = ToWrite

def _write_shops(data, Object, Content, ToWrite):
    """
    Handle writing to DataShops.json with proper structure.
    
    Args:
        data: The existing JSON data
        Object: The shop name (e.g., "ForestShop")
        Content: Specific content ("IDs" or other) or None
        ToWrite: The data to write
    """
    # Ensure the shop exists as a list
    if Object not in data:
        data[Object] = [{}]
    elif not isinstance(data[Object], list):
        data[Object] = [data[Object]]
    
    if Content == "IDs":
        # Update or add IDs to the first item
        if len(data[Object]) == 0:
            data[Object].append({"IDs": ToWrite})
        else:
            data[Object][0]["IDs"] = ToWrite
    elif Content is not None:
        # Handle writing specific shop data
        found = False
        for item in data[Object]:
            if Content in item:
                item[Content] = ToWrite
                found = True
                break
        
        if not found:
            # Add new data to the first dictionary in the list
            if len(data[Object]) > 0:
                data[Object][0][Content] = ToWrite
            else:
                data[Object].append({Content: ToWrite})
    else:
        # Overwrite the entire shop
        data[Object] = ToWrite

def _write_saves(data, Object, Content, ToWrite):
    """
    Handle writing to SaveSlots.json with null preservation.
    
    Args:
        data: The existing JSON data
        Object: The save slot (e.g., "Save1")
        Content: Specific content or None
        ToWrite: The data to write
    """
    # Ensure the save slot exists
    if Object not in data:
        data[Object] = {}
    
    if Content is not None:
        # Write specific save data
        data[Object][Content] = ToWrite
    else:
        # Overwrite the entire save slot
        data[Object] = ToWrite

def _write_generic_json(data, Object, Content, ToWrite):
    """
    Generic handler for writing to other JSON files.
    
    Args:
        data: The existing JSON data
        Object: The primary key
        Content: Secondary key or None
        ToWrite: The data to write
    """
    # Ensure the object exists
    if Object not in data:
        if Content is not None:
            data[Object] = {}
        else:
            data[Object] = ToWrite
            return
    
    if Content is not None:
        # Handle writing to potentially nested structures
        if isinstance(data[Object], list):
            # If it's a list, we need to find or create the right dict
            found = False
            for item in data[Object]:
                if isinstance(item, dict):
                    if Content in item:
                        item[Content] = ToWrite
                        found = True
                        break
            
            if not found:
                # Add to the first dict if it exists, otherwise append a new dict
                if len(data[Object]) > 0 and isinstance(data[Object][0], dict):
                    data[Object][0][Content] = ToWrite
                else:
                    data[Object].append({Content: ToWrite})
        else:
            # Simple key-value update
            data[Object][Content] = ToWrite
    else:
        # Overwrite the entire object
        data[Object] = ToWrite


