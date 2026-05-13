"""
    Fichier : 1_ImportationDumpSql.py
    Auteur : OM 2023.03.21 Connection par l'instanciation de la classe Toolsbd.

    On obtient un objet "objet_dumpbd"

    Cela permet de construire la base de donnée à partir de votre fichier DUMP en SQL
    obtenu par l'exportation de votre bd dans PhpMyAdmin.
    Le fichier .env doit être correctement paramétré. (host, user, password, nomdevotrebd)
    Le fichier DUMP de la BD doit se trouver dans le répertoire "database" de votre projet Python.

    On signale les erreurs importantes
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Permet d'exécuter ce script en "Run in terminal" depuis n'importe quel dossier
# (Cursor peut lancer le terminal dans le dossier du fichier courant).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from APP_FILMS_164.database import database_tools

try:
    objet_dumpbd = database_tools.ToolsBd().load_dump_sql_bd_init()
except Exception as erreur_load_dump_sql:
    print(f"Initialisation de la BD Impossible ! (voir DUMP ou .env) "
          f"{erreur_load_dump_sql.args[0]} , "
          f"{erreur_load_dump_sql}")
