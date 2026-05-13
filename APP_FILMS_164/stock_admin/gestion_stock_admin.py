from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import os

from flask import flash, redirect, render_template, request, session, url_for

from APP_FILMS_164 import app
from APP_FILMS_164.database.database_tools import DBconnection
from APP_FILMS_164.stock_admin.stock_config import FieldSpec, STOCK_NAV_TABLE_KEYS, TABLES, TableSpec


def _bq(name: str) -> str:
    """Identifiant MySQL sécurisé (nécessaire si le nom est un mot réservé, ex. `type`)."""
    return "`" + name.replace("`", "") + "`"


def _col_list(columns: tuple[str, ...]) -> str:
    return ", ".join(_bq(c) for c in columns)


def _stock_password() -> str:
    configured = app.config.get("STOCK_ADMIN_PASSWORD")
    if configured:
        return configured
    return os.getenv("STOCK_ADMIN_PASSWORD", "stock164")


@app.context_processor
def inject_stock_nav():
    return {
        "stock_nav_tables": [(k, TABLES[k]) for k in STOCK_NAV_TABLE_KEYS if k in TABLES],
    }


@app.before_request
def _protect_stock_routes():
    if not request.path.startswith("/stock"):
        return None
    if request.endpoint in {"stock_login"}:
        return None
    if session.get("stock_authenticated"):
        return None
    flash("Connexion requise pour accéder à la gestion stock.", "warning")
    return redirect(url_for("stock_login", next=request.path))


@app.route("/stock/login", methods=["GET", "POST"])
def stock_login():
    next_url = request.args.get("next") or request.form.get("next") or url_for("stock_home")

    if request.method == "POST":
        password = (request.form.get("password") or "").strip()
        if password == _stock_password():
            session["stock_authenticated"] = True
            flash("Connexion réussie.", "success")
            return redirect(next_url)
        flash("Mot de passe incorrect.", "danger")

    return render_template("stock/login.html", next_url=next_url)


@app.route("/stock/logout", methods=["POST"])
def stock_logout():
    session.pop("stock_authenticated", None)
    flash("Déconnexion effectuée.", "info")
    return redirect(url_for("stock_login"))


def _fk_choices(field: FieldSpec) -> list[tuple[str, str]]:
    assert field.ref_table and field.ref_pk and field.ref_label_cols
    cols = (field.ref_pk,) + tuple(field.ref_label_cols)
    cols_sql = _col_list(cols)
    sql = f"SELECT {cols_sql} FROM {field.ref_table} ORDER BY {_bq(field.ref_pk)} ASC"
    with DBconnection() as db:
        db.execute(sql)
        rows = db.fetchall()
    choices: list[tuple[str, str]] = [("", "—")]
    for r in rows:
        label = " ".join(str(r[c]) for c in field.ref_label_cols if r.get(c) is not None).strip()
        choices.append((str(r[field.ref_pk]), f"{r[field.ref_pk]} - {label}" if label else str(r[field.ref_pk])))
    return choices


def _parse_value(field: FieldSpec, raw: str | None):
    if raw is None:
        return None
    raw = raw.strip()
    if raw == "":
        return None

    if field.kind == "int" or field.kind == "fk":
        return int(raw)
    if field.kind == "decimal":
        return Decimal(raw)
    if field.kind == "year":
        return int(raw)
    if field.kind == "datetime":
        return datetime.fromisoformat(raw)
    if field.kind in ("timestamp", "text", "enum"):
        return raw
    return raw


def _is_readonly_table(spec: TableSpec) -> bool:
    """Tables affichables mais non modifiables manuellement depuis l'UI."""
    return spec.table == "t_connexion"


def _render_add_edit(table_key: str, pk_value: str | None):
    spec = TABLES[table_key]

    fk_choices: dict[str, list[tuple[str, str]]] = {}
    for f in spec.fields:
        if f.kind == "fk":
            fk_choices[f.name] = _fk_choices(f)

    row = None
    if pk_value is not None:
        assert spec.pk
        sql = f"SELECT * FROM {spec.table} WHERE {_bq(spec.pk)} = %(pk)s"
        with DBconnection() as db:
            db.execute(sql, {"pk": pk_value})
            row = db.fetchone()

    if request.method == "POST":
        values = {}
        for f in spec.fields:
            if f.readonly:
                continue
            raw = request.form.get(f.name)
            v = _parse_value(f, raw)
            if f.required and v is None:
                flash(f'Champ obligatoire: "{f.label}"', "warning")
                return render_template("stock/form.html", spec=spec, row=row, fk_choices=fk_choices)
            values[f.name] = v

        try:
            if pk_value is None:
                cols = ", ".join(_bq(k) for k in values.keys())
                params = ", ".join([f"%({k})s" for k in values.keys()])
                sql = f"INSERT INTO {spec.table} ({cols}) VALUES ({params})"
                with DBconnection() as db:
                    db.execute(sql, values)
                flash(f"{spec.label}: ajout effectué.", "success")
            else:
                assert spec.pk
                sets = ", ".join([f"{_bq(k)} = %({k})s" for k in values.keys()])
                sql = f"UPDATE {spec.table} SET {sets} WHERE {_bq(spec.pk)} = %(pk)s"
                with DBconnection() as db:
                    db.execute(sql, {**values, "pk": pk_value})
                flash(f"{spec.label}: mise à jour effectuée.", "success")
            return redirect(url_for("stock_table_list", table_key=table_key))
        except Exception as e:
            flash(f"Erreur BD: {e}", "danger")
            return render_template("stock/form.html", spec=spec, row=row, fk_choices=fk_choices)

    return render_template("stock/form.html", spec=spec, row=row, fk_choices=fk_choices)


@app.route("/stock")
def stock_home():
    tables = [(k, TABLES[k]) for k in STOCK_NAV_TABLE_KEYS if k in TABLES]
    return render_template("stock/home.html", tables=tables)


@app.route("/stock/<string:table_key>")
def stock_table_list(table_key: str):
    spec = TABLES[table_key]
    if spec.table == "t_link_produit_taille":
        return redirect(url_for("stock_link_list"))

    cols = _col_list(spec.list_columns)
    sql = f"SELECT {cols} FROM {spec.table} ORDER BY {_bq(spec.pk)} DESC"
    with DBconnection() as db:
        db.execute(sql)
        rows = db.fetchall()
    return render_template("stock/list.html", spec=spec, rows=rows)


@app.route("/stock/<string:table_key>/add", methods=["GET", "POST"])
def stock_table_add(table_key: str):
    spec = TABLES[table_key]
    if spec.table == "t_link_produit_taille":
        return redirect(url_for("stock_link_list"))
    if _is_readonly_table(spec):
        flash(f"{spec.label}: ajout manuel désactivé.", "info")
        return redirect(url_for("stock_table_list", table_key=table_key))
    return _render_add_edit(table_key, None)


@app.route("/stock/<string:table_key>/edit/<int:pk>", methods=["GET", "POST"])
def stock_table_edit(table_key: str, pk: int):
    spec = TABLES[table_key]
    if spec.table == "t_link_produit_taille":
        return redirect(url_for("stock_link_list"))
    if _is_readonly_table(spec):
        flash(f"{spec.label}: modification manuelle désactivée.", "info")
        return redirect(url_for("stock_table_list", table_key=table_key))
    return _render_add_edit(table_key, str(pk))


@app.route("/stock/<string:table_key>/delete/<int:pk>", methods=["GET", "POST"])
def stock_table_delete(table_key: str, pk: int):
    spec = TABLES[table_key]
    if spec.table == "t_link_produit_taille":
        return redirect(url_for("stock_link_list"))
    if _is_readonly_table(spec):
        flash(f"{spec.label}: suppression manuelle désactivée.", "info")
        return redirect(url_for("stock_table_list", table_key=table_key))

    assert spec.pk
    sql_select = f"SELECT * FROM {spec.table} WHERE {_bq(spec.pk)} = %(pk)s"
    with DBconnection() as db:
        db.execute(sql_select, {"pk": pk})
        row = db.fetchone()

    if request.method == "POST":
        try:
            sql_delete = f"DELETE FROM {spec.table} WHERE {_bq(spec.pk)} = %(pk)s"
            with DBconnection() as db:
                db.execute(sql_delete, {"pk": pk})
            flash(f"{spec.label}: suppression effectuée.", "success")
            return redirect(url_for("stock_table_list", table_key=table_key))
        except Exception as e:
            flash(
                "Suppression impossible (contrainte FK). Supprime d'abord les éléments liés, ou enlève la FK.",
                "danger",
            )
            flash(f"Détail: {e}", "danger")

    return render_template("stock/delete.html", spec=spec, row=row)


@app.route("/stock/sessions/new", methods=["GET", "POST"])
def stock_create_session():
    if request.method == "POST":
        nom = (request.form.get("nom") or "").strip()
        prenom = (request.form.get("prenom") or "").strip()
        mdp = (request.form.get("mot_de_passe") or "").strip()
        fk_raw = request.form.get("fk_personne") or None
        if not nom or not prenom or not mdp:
            flash("Nom, prénom et mot de passe sont obligatoires.", "warning")
        else:
            values = {
                "fk_personne": int(fk_raw) if fk_raw else None,
                "nom": nom,
                "prenom": prenom,
                "mot_de_passe": mdp,
            }
            try:
                sql = """INSERT INTO t_session (fk_personne, nom, prenom, mot_de_passe)
                         VALUES (%(fk_personne)s, %(nom)s, %(prenom)s, %(mot_de_passe)s)"""
                with DBconnection() as db:
                    db.execute(sql, values)
                flash("Session créée.", "success")
                return redirect(url_for("stock_table_list", table_key="t_session"))
            except Exception as e:
                flash(f"Erreur création session: {e}", "danger")

    return render_template("stock/session_new.html")


@app.route("/stock/liens-produit-taille", methods=["GET", "POST"])
def stock_link_list():
    spec = TABLES["t_link_produit_taille"]
    produit_field = spec.fields[0]
    taille_field = spec.fields[1]
    produits = _fk_choices(produit_field)
    tailles = _fk_choices(taille_field)

    if request.method == "POST":
        fk_produit = request.form.get("fk_produit")
        fk_taille = request.form.get("fk_taille")
        if not fk_produit or not fk_taille:
            flash("Produit et taille obligatoires.", "warning")
        else:
            try:
                sql = """INSERT INTO t_link_produit_taille (fk_produit, fk_taille)
                         VALUES (%(fk_produit)s, %(fk_taille)s)"""
                with DBconnection() as db:
                    db.execute(sql, {"fk_produit": int(fk_produit), "fk_taille": int(fk_taille)})
                flash("Association ajoutée.", "success")
            except Exception as e:
                flash(f"Erreur: {e}", "danger")

    sql = f"""SELECT l.fk_produit, p.{_bq("type")} AS produit_nom,
                    l.fk_taille, t.taille AS taille_lib
             FROM t_link_produit_taille l
             INNER JOIN t_produit p ON l.fk_produit = p.id_produit
             INNER JOIN t_taille t ON l.fk_taille = t.id_taille
             ORDER BY l.fk_produit DESC, l.fk_taille DESC"""
    with DBconnection() as db:
        db.execute(sql)
        links = db.fetchall()

    return render_template(
        "stock/link_list.html",
        spec=spec,
        links=links,
        produits=produits,
        tailles=tailles,
    )


@app.route("/stock/liens-produit-taille/delete/<int:fk_produit>/<int:fk_taille>", methods=["POST"])
def stock_link_delete(fk_produit: int, fk_taille: int):
    try:
        sql = """DELETE FROM t_link_produit_taille
                 WHERE fk_produit = %(fk_produit)s AND fk_taille = %(fk_taille)s"""
        with DBconnection() as db:
            db.execute(sql, {"fk_produit": fk_produit, "fk_taille": fk_taille})
        flash("Association supprimée.", "success")
    except Exception as e:
        flash(f"Erreur: {e}", "danger")
    return redirect(url_for("stock_link_list"))
