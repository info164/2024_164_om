from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

InputKind = Literal[
    "text",
    "int",
    "decimal",
    "year",
    "datetime",
    "timestamp",
    "enum",
    "fk",
]


@dataclass(frozen=True)
class FieldSpec:
    name: str
    label: str
    kind: InputKind
    required: bool = True
    # For FK
    ref_table: str | None = None
    ref_pk: str | None = None
    ref_label_cols: tuple[str, ...] | None = None
    # For enum
    enum_values: tuple[str, ...] | None = None
    # For readonly fields (auto timestamps)
    readonly: bool = False


@dataclass(frozen=True)
class TableSpec:
    table: str
    label: str
    pk: str | None  # None for link table with composite key
    list_columns: tuple[str, ...]
    fields: tuple[FieldSpec, ...]


# Tables affichées dans le menu « Stock » et sur /stock — pas mouvements ni liaison produit/taille
STOCK_NAV_TABLE_KEYS: Final[tuple[str, ...]] = (
    "t_session",
    "t_marque",
    "t_modele",
    "t_produit",
    "t_taille",
    "t_connexion",
)

TABLES: dict[str, TableSpec] = {
    "t_session": TableSpec(
        table="t_session",
        label="Sessions",
        pk="id_session",
        list_columns=("id_session", "fk_personne", "nom", "prenom"),
        fields=(
            FieldSpec(
                "fk_personne",
                "Réf. personne (optionnel)",
                "int",
                required=False,
            ),
            FieldSpec("nom", "Nom", "text", required=True),
            FieldSpec("prenom", "Prénom", "text", required=True),
            FieldSpec("mot_de_passe", "Mot de passe", "text", required=True),
        ),
    ),
    "t_connexion": TableSpec(
        table="t_connexion",
        label="Historique de connexion",
        pk="id_connexion",
        list_columns=("id_connexion", "fk_session", "date_debut", "date_fin"),
        fields=(
            FieldSpec(
                "fk_session",
                "Session",
                "fk",
                required=True,
                ref_table="t_session",
                ref_pk="id_session",
                ref_label_cols=("nom", "prenom"),
            ),
            FieldSpec("date_debut", "Date début", "datetime", required=True),
            FieldSpec("date_fin", "Date fin", "datetime", required=False),
        ),
    ),
    "t_marque": TableSpec(
        table="t_marque",
        label="Marques",
        pk="id_marque",
        list_columns=("id_marque", "nom"),
        fields=(FieldSpec("nom", "Nom", "text", required=True),),
    ),
    "t_modele": TableSpec(
        table="t_modele",
        label="Modèles",
        pk="id_modele",
        list_columns=("id_modele", "nom", "annee", "fk_marque"),
        fields=(
            FieldSpec("nom", "Nom", "text", required=True),
            FieldSpec("annee", "Année", "year", required=True),
            FieldSpec(
                "fk_marque",
                "Marque",
                "fk",
                required=False,
                ref_table="t_marque",
                ref_pk="id_marque",
                ref_label_cols=("nom",),
            ),
        ),
    ),
    "t_produit": TableSpec(
        table="t_produit",
        label="Produits",
        pk="id_produit",
        list_columns=("id_produit", "type", "prix", "quantite_stock", "fk_modele"),
        fields=(
            FieldSpec("type", "Type", "text", required=True),
            FieldSpec("prix", "Prix", "decimal", required=True),
            FieldSpec("quantite_stock", "Quantité en stock", "int", required=True),
            FieldSpec(
                "fk_modele",
                "Modèle",
                "fk",
                required=False,
                ref_table="t_modele",
                ref_pk="id_modele",
                ref_label_cols=("nom", "annee"),
            ),
        ),
    ),
    "t_taille": TableSpec(
        table="t_taille",
        label="Tailles",
        pk="id_taille",
        list_columns=("id_taille", "taille"),
        fields=(FieldSpec("taille", "Taille", "text", required=True),),
    ),
    "t_mouvement": TableSpec(
        table="t_mouvement",
        label="Mouvements",
        pk="id_action",
        list_columns=(
            "id_action",
            "fk_session",
            "fk_produit",
            "type_action",
            "quantite",
            "date",
        ),
        fields=(
            FieldSpec(
                "fk_session",
                "Session",
                "fk",
                required=True,
                ref_table="t_session",
                ref_pk="id_session",
                ref_label_cols=("nom", "prenom"),
            ),
            FieldSpec(
                "fk_produit",
                "Produit",
                "fk",
                required=True,
                ref_table="t_produit",
                ref_pk="id_produit",
                ref_label_cols=("type",),
            ),
            FieldSpec(
                "type_action",
                "Type d'action",
                "enum",
                required=True,
                enum_values=("DEPOT", "RETRAIT"),
            ),
            FieldSpec("quantite", "Quantité", "int", required=True),
            FieldSpec("date", "Date", "datetime", required=True),
        ),
    ),
    # Table associative — CRUD dédiée /stock/liens-produit-taille (hors menu)
    "t_link_produit_taille": TableSpec(
        table="t_link_produit_taille",
        label="Produit ↔ Taille",
        pk=None,
        list_columns=("fk_produit", "fk_taille"),
        fields=(
            FieldSpec(
                "fk_produit",
                "Produit",
                "fk",
                required=True,
                ref_table="t_produit",
                ref_pk="id_produit",
                ref_label_cols=("type",),
            ),
            FieldSpec(
                "fk_taille",
                "Taille",
                "fk",
                required=True,
                ref_table="t_taille",
                ref_pk="id_taille",
                ref_label_cols=("taille",),
            ),
        ),
    ),
}
