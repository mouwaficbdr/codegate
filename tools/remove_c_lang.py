#!/usr/bin/env python3
"""Script pour retirer toutes les références au langage C du fichier generate_challenges.py"""

import re

# Lire le fichier
with open('/home/mouwaficbdr/Code/codegate/tools/generate_challenges.py', 'r') as f:
    content = f.read()

# Pattern pour trouver et supprimer les lignes contenant "c": dans les templates
# Cette regex cherche une ligne qui commence par des espaces, puis "c":
content = re.sub(r'\n\s+"c":\s+"[^"]*(?:\\.[^"]*)*"', '', content)

# Pattern pour supprimer les lignes "c": dans les dictionnaires (pour les cas multi-lignes)
content = re.sub(r'\n\s+"c":\s+"""[^"]*(?:"{1,2}[^"])*"""', '', content)

# Pattern pour supprimer les types C: "types": {"c": {...}}
# On doit être prudent et garder la structure complète
content = re.sub(r',\s*\n\s+"types":\s*\{\s*"c":\s*\{[^}]*\}\s*\}', '', content)

# Écrire le résultat
with open('/home/mouwaficbdr/Code/codegate/tools/generate_challenges.py', 'w') as f:
    f.write(content)

print("✓ Références au langage C supprimées de generate_challenges.py")
