import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import IntegrityError
from config import DB_CONFIG
from db import get_connection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        pwd   = request.form.get('password', '').strip()

        # Обмеження на довжину
        if not login or not pwd:
            flash('Заповніть всі поля', 'error')
        elif len(login) > 50:
            flash('Логін не може перевищувати 50 символів', 'error')
        elif len(pwd) > 50:
            flash('Пароль не може перевищувати 50 символів', 'error')

        # Дозволені символи: літери, цифри, нижнє підкреслення, тире
        elif not re.match(r'^[a-zA-Z0-9_-]+$', login):
            flash('Логін може містити лише латинські літери, цифри, підкреслення або тире', 'error')
        elif not re.match(r'^[a-zA-Z0-9!@#$%^&*()_\-+=]+$', pwd):
            flash('Пароль повинен містити лише латинські літери, цифри та спецсимволи !@#$%^&*()-+=', 'error')

        else:
            hashed = generate_password_hash(pwd)
            try:
                conn = get_connection(DB_CONFIG['database'])
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (login, password_hash) VALUES (%s, %s)",
                    (login, hashed)
                )
                cur.close()
                conn.close()
                flash('Реєстрація успішна. Увійдіть, будь ласка.', 'success')
                return redirect(url_for('auth.login'))
            except IntegrityError:
                flash('Користувач із таким логіном уже існує', 'error')
            except Exception as e:
                flash(f'Помилка реєстрації: {e}', 'error')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        pwd   = request.form.get('password', '').strip()

        conn = get_connection(DB_CONFIG['database'])
        cur  = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE login = %s",
            (login,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and check_password_hash(row[1], pwd):
            session.clear()
            session['user_id'] = row[0]
            session['login']   = login
            return redirect(url_for('classify.index'))
        else:
            flash('Невірний логін або пароль', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    # Повертаємо на сторінку входу з правильним ендпоінтом
    return redirect(url_for('auth.login'))
