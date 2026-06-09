# routes.py
from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
from config import db
from controllers.db_conversor import Conversor
from models.database.db_usuario import Usuario
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='views')


def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html', pagina='index')

    @app.route('/perfil', methods=['GET', 'POST'])
    def perfil():
        lerUsuario = Usuario.query.all()
        return render_template('perfil.html', lerUsuario=lerUsuario, pagina='perfil')

    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        if request.method == "POST":
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                msgUsuario = Markup("Usuário já cadastrado. Faça o login")
                flash(msgUsuario, 'danger')
                return redirect(url_for('cadastro'))
            senha_hash = generate_password_hash(senha, method='scrypt')
            novousuario = Usuario(
                email=email, senha=senha_hash, nome=nome, permissao=None)
            db.session.add(novousuario)
            db.session.commit()
            msgCad = Markup("Cadastro realizado com sucesso!")
            flash(msgCad, 'sucesss')
            return redirect(url_for('cadastro'))
        return render_template('cadastro.html', pagina='cadastro')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "POST":
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            usuario = Usuario.query.filter_by(email=email, nome=nome).first()
            if usuario:
                if check_password_hash(usuario.senha, senha):
                    session['usuario_id'] = usuario.id
                    session['usuario_nome'] = usuario.nome
                    session['usuario_email'] = usuario.email
                    msgLogin = "Login realizado"
                    flash(msgLogin, 'sucess')
                    redirect(url_for('index'))
                else:
                    msgLogin = "Login não autorizado"
                    flash(msgLogin, 'danger')
        return render_template('login.html', pagina='login')
    @app.route('/editar', methods=['GET','POST'])
    def editar():
        if 'usuario_id' not in session:
            return redirect(url_for('login'))

        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario:
            session.clear()
            return redirect(url_for('login'))

        dados = request.form.to_dict()

        if not check_password_hash(usuario.senha, dados.get('senha_atual', '')):
            flash('Senha atual incorreta.', 'erro')
            return redirect(url_for('perfil'))

        usuario.nome = dados['nome']
        usuario.email = dados['email']
        if dados.get('senha', '').strip():
            usuario.senha = generate_password_hash(dados['senha'])

        db.session.commit()
        
        session['usuario_nome'] = usuario.nome
        session['usuario_email'] = usuario.email

        flash('Perfil atualizado com sucesso!', 'sucesso')
        return redirect(url_for('perfil'))

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/deletar', methods=['GET', 'POST'])
    def deletar():
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario:
            session.clear()
            return redirect(url_for('login'))

        senha_atual = request.form.get('senha_atual', '')
        if not check_password_hash(usuario.senha, senha_atual):
            flash('Senha atual incorreta. Conta não foi deletada.', 'erro')
            return redirect(url_for('perfil'))

        db.session.delete(usuario)
        db.session.commit()
        session.clear()

        flash('Conta deletada com sucesso.', 'sucesso')
        return redirect(url_for('cadastro'))

    @app.route('/mapa')
    def mapa():
        gdf_uniao, gdf_lito, gdf_estados = Conversor.postgis_to_gdf()
        map_html = Conversor.gdf_to_html(
            gdf_uniao, gdf_lito, gdf_estados,
            camada_nome="Áreas Classificadas",
            geojson_path="static/database/minas.geojson"
        )
        return render_template('mapa.html', mapa_html=map_html, pagina='mapa')
