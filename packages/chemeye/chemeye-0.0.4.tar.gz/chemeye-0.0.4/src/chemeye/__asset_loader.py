from importlib import resources
import json


with resources.open_text('chemeye.assets', 'default_simmat_options.json') as f:
    default_simmat_options = json.load(f)
