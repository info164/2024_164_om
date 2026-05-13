"""Gestion des "routes" FLASK et des données pour les genres.
Fichier : gestion_genres_crud.py
Auteur : OM 2021.03.16
"""
from pathlib import Path

from flask import flash
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from APP_FILMS_164 import app
from APP_FILMS_164.database.database_tools import DBconnection
from APP_FILMS_164.erreurs.exceptions import *
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFAjouterGenres
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFDeleteGenre
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFUpdateGenre

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /genres_afficher
    
    Test : ex : http://127.0.0.1:5575/genres_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                id_genre_sel = 0 >> tous les genres.
                id_genre_sel = "n" affiche le genre dont l'id est "n"
"""


@app.route("/genres_afficher/<string:order_by>/<int:id_genre_sel>", methods=['GET', 'POST'])
def genres_afficher(order_by, id_genre_sel):
    if request.method == "GET":
        try:
            with DBconnection() as mc_afficher:
                if order_by == "ASC" and id_genre_sel == 0:
                    strsql_genres_afficher = """SELECT id_produit, prix, quantite_stock, `type` AS nom, fk_modele
                                                 FROM t_produit ORDER BY id_produit ASC"""
                    mc_afficher.execute(strsql_genres_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_genre"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id sélectionné avec un nom de variable
                    valeur_id_selected_dictionnaire = {"value_id_selected": id_genre_sel}
                    strsql_genres_afficher = """SELECT id_produit, prix, quantite_stock, `type` AS nom, fk_modele
                                                FROM t_produit
                                                WHERE id_produit = %(value_id_selected)s"""

                    mc_afficher.execute(strsql_genres_afficher, valeur_id_selected_dictionnaire)
                else:
                    strsql_genres_afficher = """SELECT id_produit, prix, quantite_stock, `type` AS nom, fk_modele
                                                FROM t_produit
                                                ORDER BY id_produit DESC"""

                    mc_afficher.execute(strsql_genres_afficher)

                data_genres = mc_afficher.fetchall()

                print("data_genres ", data_genres, " Type : ", type(data_genres))

                # Différencier les messages si la table est vide.
                if not data_genres and id_genre_sel == 0:
                    flash("""La table "t_produit" est vide. !!""", "warning")
                elif not data_genres and id_genre_sel > 0:
                    # Si l'utilisateur change l'id_genre dans l'URL et que le genre n'existe pas,
                    flash(f"Le produit demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_genre" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données produits affichés !!", "success")

        except Exception as Exception_genres_afficher:
            raise ExceptionGenresAfficher(f"fichier : {Path(__file__).name}  ;  "
                                          f"{genres_afficher.__name__} ; "
                                          f"{Exception_genres_afficher}")

    # Envoie la page "HTML" au serveur.
    return render_template("genres/genres_afficher.html", data=data_genres)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /genres_ajouter
    
    Test : ex : http://127.0.0.1:5575/genres_ajouter
    
    Paramètres : sans
    
    But : Ajouter un genre pour un film
    
    Remarque :  Dans le champ "name_genre_html" du formulaire "genres/genres_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/genres_ajouter", methods=['GET', 'POST'])
def genres_ajouter_wtf():
    form = FormWTFAjouterGenres()
    if request.method == "POST":
        try:
            if form.validate_on_submit():
                nom_produit = form.nom_produit_wtf.data
                prix = form.prix_wtf.data
                quantite_stock = form.quantite_stock_wtf.data
                fk_modele = form.fk_modele_wtf.data or None

                valeurs_insertion_dictionnaire = {
                    "value_nom": nom_produit,
                    "value_prix": prix,
                    "value_quantite_stock": quantite_stock,
                    "value_fk_modele": fk_modele,
                }
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_insert = """INSERT INTO t_produit (prix, quantite_stock, `type`, fk_modele)
                                   VALUES (%(value_prix)s, %(value_quantite_stock)s, %(value_nom)s, %(value_fk_modele)s)"""
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(strsql_insert, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('genres_afficher', order_by='DESC', id_genre_sel=0))

        except Exception as Exception_genres_ajouter_wtf:
            raise ExceptionGenresAjouterWtf(f"fichier : {Path(__file__).name}  ;  "
                                            f"{genres_ajouter_wtf.__name__} ; "
                                            f"{Exception_genres_ajouter_wtf}")

    return render_template("genres/genres_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /genre_update
    
    Test : ex cliquer sur le menu "genres" puis cliquer sur le bouton "EDIT" d'un "genre"
    
    Paramètres : sans
    
    But : Editer(update) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_update_wtf" du formulaire "genres/genre_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/genre_update", methods=['GET', 'POST'])
def genre_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_genre"
    id_genre_update = request.values['id_genre_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateGenre()
    try:
        # 2023.05.14 OM S'il y a des listes déroulantes dans le formulaire
        # La validation pose quelques problèmes
        if request.method == "POST" and form_update.submit.data:
            nom_produit = form_update.nom_produit_update_wtf.data
            prix = form_update.prix_update_wtf.data
            quantite_stock = form_update.quantite_stock_update_wtf.data
            fk_modele = form_update.fk_modele_update_wtf.data or None

            valeur_update_dictionnaire = {
                "value_id_produit": id_genre_update,
                "value_nom": nom_produit,
                "value_prix": prix,
                "value_quantite_stock": quantite_stock,
                "value_fk_modele": fk_modele,
            }
            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update = """UPDATE t_produit
                                SET `type` = %(value_nom)s,
                                    prix = %(value_prix)s,
                                    quantite_stock = %(value_quantite_stock)s,
                                    fk_modele = %(value_fk_modele)s
                                WHERE id_produit = %(value_id_produit)s"""
            with DBconnection() as mconn_bd:
                mconn_bd.execute(str_sql_update, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_genre_update"
            return redirect(url_for('genres_afficher', order_by="ASC", id_genre_sel=id_genre_update))
        elif request.method == "GET":
            str_sql_select_produit = """SELECT id_produit, `type` AS nom, prix, quantite_stock, fk_modele
                                        FROM t_produit
                                        WHERE id_produit = %(value_id_produit)s"""
            valeur_select_dictionnaire = {"value_id_produit": id_genre_update}
            with DBconnection() as mybd_conn:
                mybd_conn.execute(str_sql_select_produit, valeur_select_dictionnaire)
                data_produit = mybd_conn.fetchone()

            # Afficher la valeur sélectionnée dans les champs du formulaire "genre_update_wtf.html"
            form_update.nom_produit_update_wtf.data = data_produit["nom"]
            form_update.prix_update_wtf.data = data_produit["prix"]
            form_update.quantite_stock_update_wtf.data = data_produit["quantite_stock"]
            form_update.fk_modele_update_wtf.data = data_produit["fk_modele"]

    except Exception as Exception_genre_update_wtf:
        raise ExceptionGenreUpdateWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{genre_update_wtf.__name__} ; "
                                      f"{Exception_genre_update_wtf}")

    return render_template("genres/genre_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /genre_delete
    
    Test : ex. cliquer sur le menu "genres" puis cliquer sur le bouton "DELETE" d'un "genre"
    
    Paramètres : sans
    
    But : Effacer(delete) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_delete_wtf" du formulaire "genres/genre_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@app.route("/genre_delete", methods=['GET', 'POST'])
def genre_delete_wtf():
    data_objets_associes = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_genre"
    id_genre_delete = request.values['id_genre_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteGenre()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("genres_afficher", order_by="ASC", id_genre_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_objets_associes = session.get('data_objets_associes', None)
                print("data_objets_associes ", data_objets_associes)

                flash(f"Effacer le produit de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer produit" qui va irrémédiablement EFFACER le produit
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_id_produit": id_genre_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_actions = """DELETE FROM t_mouvement WHERE fk_produit = %(value_id_produit)s"""
                str_sql_delete_link_taille = """DELETE FROM t_link_produit_taille WHERE fk_produit = %(value_id_produit)s"""
                str_sql_delete_produit = """DELETE FROM t_produit WHERE id_produit = %(value_id_produit)s"""
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(str_sql_delete_actions, valeur_delete_dictionnaire)
                    mconn_bd.execute(str_sql_delete_link_taille, valeur_delete_dictionnaire)
                    mconn_bd.execute(str_sql_delete_produit, valeur_delete_dictionnaire)

                flash(f"Produit définitivement effacé !!", "success")
                print(f"Produit définitivement effacé !!")

                # afficher les données
                return redirect(url_for('genres_afficher', order_by="ASC", id_genre_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_id_produit": id_genre_delete}
            print(id_genre_delete, type(id_genre_delete))

            with DBconnection() as mydb_conn:
                str_sql_associes = """SELECT CONCAT('Mouvement #', id_action, ' (fk_session=', fk_session, ')') AS description_assoc
                                      FROM t_mouvement
                                      WHERE fk_produit = %(value_id_produit)s
                                      UNION ALL
                                      SELECT CONCAT('Taille liée fk_taille=', fk_taille) AS description_assoc
                                      FROM t_link_produit_taille
                                      WHERE fk_produit = %(value_id_produit)s"""
                mydb_conn.execute(str_sql_associes, valeur_select_dictionnaire)
                data_objets_associes = mydb_conn.fetchall()
                print("data_objets_associes...", data_objets_associes)

                # Nécessaire pour mémoriser les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                session['data_objets_associes'] = data_objets_associes

                str_sql_produit = """SELECT id_produit, `type` AS nom FROM t_produit WHERE id_produit = %(value_id_produit)s"""
                mydb_conn.execute(str_sql_produit, valeur_select_dictionnaire)
                data_produit = mydb_conn.fetchone()

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_delete_wtf.html"
            form_delete.nom_produit_delete_wtf.data = data_produit["nom"]

            # Le bouton pour l'action "DELETE" dans le form. "genre_delete_wtf.html" est caché.
            btn_submit_del = False

    except Exception as Exception_genre_delete_wtf:
        raise ExceptionGenreDeleteWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{genre_delete_wtf.__name__} ; "
                                      f"{Exception_genre_delete_wtf}")

    return render_template("genres/genre_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_objets_associes=data_objets_associes)
