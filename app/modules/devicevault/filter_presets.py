import json
import os
from app.core.paths import get_filter_presets_path
from app.core.logger import logger


def load_presets():
    """Load saved filter presets from local JSON file."""
    path = get_filter_presets_path()
    if not os.path.exists(path):
        return {"presets": []}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) and "presets" in data else {"presets": []}
    except Exception as e:
        logger.error(f"Failed to load filter presets: {e}")
        return {"presets": []}


def save_presets(presets_data):
    """Save presets to local JSON file."""
    path = get_filter_presets_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(presets_data, f, indent=2, ensure_ascii=False)
        logger.info("Filter presets saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save filter presets: {e}")
        return False


def add_preset(name, filters):
    """Add or update a preset."""
    data = load_presets()
    presets = data["presets"]
    
    # Check if name exists
    for p in presets:
        if p["name"].lower() == name.lower():
            p.update(filters)
            break
    else:
        preset = {"name": name}
        preset.update(filters)
        presets.append(preset)
    
    data["presets"] = presets
    return save_presets(data)


def delete_preset(name):
    """Delete a preset by name."""
    data = load_presets()
    presets = [p for p in data["presets"] if p["name"].lower() != name.lower()]
    data["presets"] = presets
    return save_presets(data)


def get_preset(name):
    """Get a specific preset by name."""
    data = load_presets()
    for p in data["presets"]:
        if p["name"].lower() == name.lower():
            return p
    return None


def get_all_preset_names():
    """Return list of preset names for dropdown."""
    data = load_presets()
    return [p["name"] for p in data["presets"]]
