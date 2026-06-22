
from functools import lru_cache

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from markupsafe import Markup

from controllers.map_builder import MapBuilder
from extensions import db
from models.user import User

bp = Blueprint("main", __name__)

MINE_GEOJSON_PATH = "static/database/minas.geojson"


def init_app(app):
    app.register_blueprint(bp)


@bp.route("/")
def index():
    return render_template("index.html", pagina="index")


@bp.route("/perfil", methods=["GET"])
@login_required
def perfil():
    return render_template("perfil.html", pagina="profile")


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        if User.query.filter_by(email=email).first():
            flash(Markup("Usuário já cadastrado. Faça o login"), "danger")
            return redirect(url_for("main.cadastro"))

        novo_usuario = User(name=nome, email=email)
        novo_usuario.set_password(senha)
        db.session.add(novo_usuario)
        db.session.commit()

        flash(Markup("Cadastro realizado com sucesso!"), "success")
        return redirect(url_for("main.cadastro"))

    return render_template("cadastro.html", pagina="auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = User.query.filter_by(email=email, name=nome).first()
        if usuario and usuario.check_password(senha):
            login_user(usuario)
            flash("Login realizado", "success")
            return redirect(url_for("main.index"))

        flash("Login não autorizado", "danger")

    return render_template("login.html", pagina="auth")


@bp.route("/editar", methods=["POST"])
@login_required
def editar():
    dados = request.form.to_dict()

    if not current_user.check_password(dados.get("senha_atual", "")):
        flash("Senha atual incorreta.", "danger")
        return redirect(url_for("main.perfil"))

    current_user.name = dados["nome"]
    current_user.email = dados["email"]
    nova_senha = dados.get("senha", "").strip()
    if nova_senha:
        current_user.set_password(nova_senha)

    db.session.commit()
    flash("Perfil atualizado com sucesso!", "success")
    return redirect(url_for("main.perfil"))


@bp.route("/deletar", methods=["POST"])
@login_required
def deletar():
    senha_atual = request.form.get("senha_atual", "")
    if not current_user.check_password(senha_atual):
        flash("Senha atual incorreta. Conta não foi deletada.", "danger")
        return redirect(url_for("main.perfil"))

    db.session.delete(current_user)
    db.session.commit()
    logout_user()

    flash("Conta deletada com sucesso.", "success")
    return redirect(url_for("main.cadastro"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@lru_cache(maxsize=1)
def construtor_mapa_html() -> str:
    merged_gdf, lithology_gdf, states_gdf = MapBuilder.load_layers()
    return MapBuilder.build_map_html(
        merged_gdf,
        lithology_gdf,
        states_gdf,
        layer_name="Áreas Classificadas",
        mine_geojson_paths=MINE_GEOJSON_PATH,
    )


@bp.route("/mapa")
def mapa():
    return render_template("mapa.html", mapa_html=construtor_mapa_html(), pagina="map")
