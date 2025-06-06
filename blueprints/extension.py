import math

from flask import Blueprint, render_template, session, redirect, url_for, request, current_app, flash

from config import DB_CONFIG
from db import get_connection

extension_bp = Blueprint('extension', __name__, template_folder='templates')


@extension_bp.route('/extension')
def extension():
    """
    Одна сторінка: показує інструкцію або список результатів для адміна.
    """
    if 'user_id' not in session:
        return render_template('extension.html')

    is_admin = session.get('login') == 'admin'

    if not is_admin:
        return render_template('extension.html')

    # Якщо адмін — показуємо таблицю результатів
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    try:
        conn = get_connection(DB_CONFIG['database'])
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM extension_results")
        total = cur.fetchone()[0]

        cur.execute(
            "SELECT id, title, probability, is_clickbait "
            "FROM extension_results "
            "ORDER BY id DESC "
            "LIMIT %s OFFSET %s",
            (per_page, offset)
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        total_pages = math.ceil(total / per_page) if total > 0 else 1

    except Exception as e:
        current_app.logger.error(f"[Error] Не вдалося отримати результати: {e}")
        rows = []
        total_pages = 1
        page = 1

    return render_template(
        'extension.html',
        results=rows,
        page=page,
        total_pages=total_pages,
        is_admin=True
    )


@extension_bp.route('/extension/delete/<int:result_id>', methods=['POST'])
def delete_result(result_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    is_admin = session.get('login') == 'admin'

    try:
        conn = get_connection(DB_CONFIG['database'])
        conn.autocommit = True
        cur = conn.cursor()

        if is_admin:
            cur.execute("DELETE FROM extension_results WHERE id = %s", (result_id,))
        else:
            cur.execute(
                "DELETE FROM extension_results WHERE id = %s AND user_login = %s",
                (result_id, session['login'])
            )

        cur.close()
        conn.close()

    except Exception as e:
        current_app.logger.error(f"[Error] Не вдалося видалити запис: {e}")
        flash('Не вдалося видалити запис', 'error')

    return redirect(url_for('extension.extension'))
