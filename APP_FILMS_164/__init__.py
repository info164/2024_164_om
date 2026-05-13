"""Initialisation des variables d'environnement
    Auteur : OM 2023.03.21 Indispensable pour définir les variables indispensables dans tout le projet.
"""
import sys

from environs import Env
from flask import Flask

try:
    try:
        obj_env = Env()
        obj_env.read_env()
        HOST_MYSQL = obj_env("HOST_MYSQL")
        USER_MYSQL = obj_env("USER_MYSQL")
        PASS_MYSQL = obj_env("PASS_MYSQL")
        PORT_MYSQL = int(obj_env("PORT_MYSQL"))
        NAME_BD_MYSQL = obj_env("NAME_BD_MYSQL")
        NAME_FILE_DUMP_SQL_BD = obj_env("NAME_FILE_DUMP_SQL_BD")

        ADRESSE_SRV_FLASK = obj_env("ADRESSE_SRV_FLASK")
        DEBUG_FLASK = obj_env("DEBUG_FLASK")
        PORT_FLASK = int(obj_env("PORT_FLASK"))
        SECRET_KEY_FLASK = obj_env("SECRET_KEY_FLASK")
        STOCK_ADMIN_PASSWORD = obj_env("STOCK_ADMIN_PASSWORD", "stock164")

        # OM 2022.04.11 Début de l'application
        app = Flask(__name__, template_folder="templates")
        app.config["STOCK_ADMIN_PASSWORD"] = STOCK_ADMIN_PASSWORD
        print("app.url_map ____> ", app.url_map)

    except Exception as erreur:
        print(f"45677564530 init application variables d'environnement ou avec le fichier (son nom, son contenu)\n"
              f"{__name__}, "
              f"{erreur.args[0]}, "
              f"{repr(erreur)}, "
              f"{type(erreur)}")
        sys.exit()

    """
        Tout commence ici. Il faut "indiquer" les routes de l'applicationn.    
        Dans l'application les lignes ci-dessous doivent se trouver ici... soit après l'instanciation de la classe "Flask"
    """
    from APP_FILMS_164.database import database_tools
    from APP_FILMS_164.essais_wtf_forms import gestion_essai_wtf
    from APP_FILMS_164.essais_wtf_forms import gestion_wtf_forms_demo_select
    from APP_FILMS_164.genres import gestion_genres_crud
    from APP_FILMS_164.demos_om_164 import routes_demos

    from APP_FILMS_164.films_genres import gestion_films_genres_crud
    from APP_FILMS_164.erreurs import msg_avertissements

    from APP_FILMS_164.films import gestion_films_crud
    from APP_FILMS_164.films import gestion_films_wtf_forms
    from APP_FILMS_164.stock_admin import gestion_stock_admin

except Exception as Exception_init_app_films_164:
    print(f"4567756434 Une erreur est survenue {type(Exception_init_app_films_164)} dans"
          f"__init__ {Exception_init_app_films_164.args}")
    sys.exit()
