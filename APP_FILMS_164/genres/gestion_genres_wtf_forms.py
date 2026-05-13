"""
    Fichier : gestion_genres_wtf_forms.py
    Auteur : OM 2021.03.22
    Gestion des formulaires avec WTF
"""
from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp


class FormWTFAjouterGenres(FlaskForm):
    """
        Formulaire adapté à la table t_produit.
    """
    nom_produit_regexp = r"^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ0-9]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ0-9]+$"
    nom_produit_wtf = StringField(
        "Type de produit",
        validators=[
            Length(min=2, max=50, message="min 2 max 50"),
            Regexp(
                nom_produit_regexp,
                message="Pas de caractères spéciaux (ok: espace, apostrophe, trait d'union).",
            ),
        ],
    )
    prix_wtf = DecimalField("Prix", places=2, validators=[DataRequired("Prix obligatoire"), NumberRange(min=0)])
    quantite_stock_wtf = IntegerField(
        "Quantité en stock", validators=[DataRequired("Quantité obligatoire"), NumberRange(min=0, max=32767)]
    )
    fk_modele_wtf = IntegerField("Id modèle (optionnel)", validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Enregistrer produit")


class FormWTFUpdateGenre(FlaskForm):
    """
        Formulaire adapté à la table t_produit.
    """
    nom_produit_update_regexp = r"^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ0-9]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ0-9]+$"
    nom_produit_update_wtf = StringField(
        "Type de produit",
        validators=[
            Length(min=2, max=50, message="min 2 max 50"),
            Regexp(
                nom_produit_update_regexp,
                message="Pas de caractères spéciaux (ok: espace, apostrophe, trait d'union).",
            ),
        ],
    )
    prix_update_wtf = DecimalField("Prix", places=2, validators=[DataRequired("Prix obligatoire"), NumberRange(min=0)])
    quantite_stock_update_wtf = IntegerField(
        "Quantité en stock", validators=[DataRequired("Quantité obligatoire"), NumberRange(min=0, max=32767)]
    )
    fk_modele_update_wtf = IntegerField("Id modèle (optionnel)", validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Mettre à jour produit")


class FormWTFDeleteGenre(FlaskForm):
    """
        Dans le formulaire "genre_delete_wtf.html"

        nom_produit_delete_wtf : Champ qui reçoit la valeur du produit, lecture seule. (readonly=true)
        submit_btn_del : Bouton d'effacement "DEFINITIF".
        submit_btn_conf_del : Bouton de confirmation pour effacer un "produit".
        submit_btn_annuler : Bouton qui permet d'afficher la liste.
    """
    nom_produit_delete_wtf = StringField("Effacer ce produit")
    submit_btn_del = SubmitField("Effacer produit")
    submit_btn_conf_del = SubmitField("Etes-vous sur d'effacer ?")
    submit_btn_annuler = SubmitField("Annuler")
