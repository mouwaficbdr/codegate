#!/usr/bin/env python3
"""Script pour retirer proprement toutes les références au langage C"""

import re

# Lire le fichier
with open('/home/mouwaficbdr/Code/codegate/tools/generate_challenges.py', 'r') as f:
    lines = f.readlines()

# Nouvelle approche : parcourir ligne par ligne
new_lines = []
skip_until_comma = False
i = 0

while i < len(lines):
    line = lines[i]
    
    # Détecter le début d'une clé "c" dans templates ou types
    if re.match(r'\s*"c":\s*"', line) or re.match(r'\s*"c":\s*\{', line):
        # Compter les guillemets/accolades pour savoir où ça se termine
        if '"c":' in line and '{' in line:
            # C'est un type avec accolade genre "c": { ... }
            bracket_count = line.count('{') - line.count('}')
            i += 1
            while i < len(lines) and bracket_count > 0:
                bracket_count += lines[i].count('{') - lines[i].count('}') 
                i += 1
            # Supprimer aussi la virgule qui précède si elle existe
            if new_lines and new_lines[-1].rstrip().endswith(','):
                new_lines[-1] = new_lines[-1].rstrip()[:-1] + '\n'
        elif '"c":' in line:
            # C'est un template sur une seule ligne
            i += 1
            # Supprimer aussi la virgule qui suit s'il y en a une
            if i < len(lines) and lines[i].strip() == '':
                new_lines.pop() if new_lines and ',' in new_lines[-1] else None

        continue  # Ne pas ajouter cette ligne
    
    # Vérifier si c'est une ligne "types" qui ne contient que "c"
    if re.match(r'\s*"types":\s*\{\s*"c":', line):
        # Supprimer toute la clé types
        bracket_count = line.count('{') - line.count('}')
        i += 1
        while i < len(lines) and bracket_count > 0:
            bracket_count += lines[i].count('{') - lines[i].count('}')
            i += 1
        # Supprimer la virgule précédente
        if new_lines and new_lines[-1].rstrip().endswith(','):
            new_lines[-1] = new_lines[-1].rstrip()[:-1] + '\n'
        continue
    
    new_lines.append(line)
    i += 1

# Écrire le résultat
with open('/home/mouwaficbdr/Code/codegate/tools/generate_challenges.py', 'w') as f:
    f.writelines(new_lines)

print("✓ Références C suppr imées proprement")
