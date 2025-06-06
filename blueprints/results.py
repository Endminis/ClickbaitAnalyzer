import math
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash

from config import DB_CONFIG
from db import get_connection

results_bp = Blueprint('results', __name__)


@results_bp.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    is_admin = session.get('login') == 'admin'

    try:
        conn = get_connection(DB_CONFIG['database'])
        cur = conn.cursor()

        if is_admin:
            cur.execute("SELECT COUNT(*) FROM classification_results")
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT id, user_login, title, probability, is_clickbait "
                "FROM classification_results "
                "ORDER BY id DESC "
                "LIMIT %s OFFSET %s",
                (per_page, offset)
            )
        else:
            cur.execute(
                "SELECT COUNT(*) FROM classification_results WHERE user_login = %s",
                (session['login'],)
            )
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT id, user_login, title, probability, is_clickbait "
                "FROM classification_results "
                "WHERE user_login = %s "
                "ORDER BY id DESC "
                "LIMIT %s OFFSET %s",
                (session['login'], per_page, offset)
            )

        rows = cur.fetchall()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        cur.close()
        conn.close()
    except Exception as e:
        current_app.logger.error(f"[Error] Не вдалося отримати результати: {e}")
        rows = []
        total_pages = 1
        page = 1

    return render_template(
        'results.html',
        results=rows,
        page=page,
        total_pages=total_pages,
        is_admin=is_admin
    )


@results_bp.route('/results/delete/<int:result_id>', methods=['POST'])
def delete_result(result_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    is_admin = session.get('login') == 'admin'

    try:
        conn = get_connection(DB_CONFIG['database'])
        conn.autocommit = True
        cur = conn.cursor()

        if is_admin:
            cur.execute("DELETE FROM classification_results WHERE id = %s", (result_id,))
        else:
            cur.execute(
                "DELETE FROM classification_results WHERE id = %s AND user_login = %s",
                (result_id, session['login'])
            )

        cur.close()
        conn.close()
    except Exception as e:
        current_app.logger.error(f"[Error] Не вдалося видалити запис: {e}")
        flash('Не вдалося видалити запис', 'error')

    return redirect(url_for('results.results'))
