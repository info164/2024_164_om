"""
    Fichier : gestion_wtf_forms_demo_select.py
    Auteur : OM 2023.03.26
    Gestions des "routes" FLASK et des données pour des démos sur les listes déroulantes.
"""
import sys

import pymysql
from flask import flash, redirect, url_for
from flask import render_template
from flask import request
from flask import session

from APP_FILMS_164 import app
from APP_FILMS_164.database.database_tools import DBconnection
from APP_FILMS_164.erreurs.msg_erreurs import *
from APP_FILMS_164.essais_wtf_forms.wtf_forms_demo_select import DemoFormSelectWTF

"""
    Auteur : OM 2023.03.26
    Définition d'une "route" /demo_select_wtf
    
    Test : 
    
    Paramètres : sans
    
    But : Montrer qu'il est possible de faire des listes déroulantes-
    
    Remarque :  
"""


@app.route("/demo_select_wtf", methods=['GET', 'POST'])
def demo_select_wtf():
    genre_selectionne = None
    # Objet formulaire pour montrer une liste déroulante basé su    r la table "t_genre"
    form_demo = DemoFormSelectWTF()
    try:
        print("form_demo.submit_btn_ok_dplist_genre.data  ", form_demo.submit_btn_ok_dplist_genre.data)
        if request.method == "POST" and form_demo.submit_btn_ok_dplist_genre.data:

            if form_demo.submit_btn_ok_dplist_genre.data:
                print("Genre sélectionné : ",
                      form_demo.genres_dropdown_wtf.data)
                genre_selectionne = form_demo.genres_dropdown_wtf.data
                form_demo.genres_dropdown_wtf.choices = session['genre_val_list_dropdown']
                data_genres = session['data_genres']
                return render_template("zzz_essais_om_104/demo_form_select_wtf.html",
                                       form=form_demo,
                                       genre_selectionne=genre_selectionne,
                                       data_genres_drop_down=data_genres)


        if request.method == "GET":
            with DBconnection() as mc_afficher:
                strsql_genres_afficher = """SELECT id_genre, intitule_genre FROM t_genre ORDER BY id_genre ASC"""
                mc_afficher.execute(strsql_genres_afficher)

            data_genres = mc_afficher.fetchall()
            session['data_genres'] = data_genres
            print("demo_select_wtf data_genres ", data_genres, " Type : ", type(data_genres))

            """
                Préparer les valeurs pour la liste déroulante de l'objet "form_demo"
                la liste déroulante est définie dans le "wtf_forms_demo_select.py" 
                le formulaire qui utilise la liste déroulante "zzz_essais_om_104/demo_form_select_wtf.html"
            """
            genre_val_list_dropdown = []
            for i in data_genres:
                genre_val_list_dropdown.append(i['intitule_genre'])

            # Aussi possible d'avoir un id numérique et un texte en correspondance
            # genre_val_list_dropdown = [(i["id_genre"], i["intitule_genre"]) for i in data_genres]

            print("genre_val_list_dropdown ", genre_val_list_dropdown)

            form_demo.genres_dropdown_wtf.choices = genre_val_list_dropdown
            session['genre_val_list_dropdown'] = genre_val_list_dropdown
            # Ceci est simplement une petite démo. on fixe la valeur PRESELECTIONNEE de la liste
            form_demo.genres_dropdown_wtf.data = "philosophique"
            genre_selectionne = form_demo.genres_dropdown_wtf.data
            print("genre choisi dans la liste :", genre_selectionne)
            session['genre_selectionne_get'] = genre_selectionne

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans wtf_forms_demo_select : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans wtf_forms_demo_select : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")

        flash(f"Erreur dans wtf_forms_demo_select : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")

        flash(f"__KeyError dans wtf_forms_demo_select : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("zzz_essais_om_104/demo_form_select_wtf.html",
                           form=form_demo,
                           genre_selectionne=genre_selectionne,
                           data_genres_drop_down=data_genres)


@app.route("/demo_select_dropdown", methods=['GET', 'POST'])
def demo_select_dropdown():
    """Démo POST sur une liste déroulante HTML (sans librairie UI externe)."""
    choice = None
    if request.method == 'POST':
        choix_list_drop_down = request.form.getlist("ma_petite_liste_unique")
        print("choix_list_drop_down ", choix_list_drop_down)
        if choix_list_drop_down:
            choice = choix_list_drop_down[0]
        elif "ma_petite_liste_unique" in request.form:
            choice = request.form["ma_petite_liste_unique"]
        print("genre choisi dans la liste :", choice)

    return render_template("zzz_essais_om_104/essai_form_result_dropdown.html",
                           my_choice_dropdown=choice,
                           liste_choice="essai")
