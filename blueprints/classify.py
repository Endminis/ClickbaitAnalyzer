from flask import Blueprint, render_template, request, session, flash, current_app, url_for, redirect

from config import DB_CONFIG
from predict import predict_clickbait
from utils.text_utils import clean_text, contains_cyrillic, has_minimum_words
from db import get_connection

classify_bp = Blueprint('classify', __name__)


@classify_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    title_raw = ''
    result = None
    probability = None

    if request.method == 'POST':
        title_raw = request.form.get('title', '').strip()
        title_clean = clean_text(title_raw)

        # Валідація тексту
        if not contains_cyrillic(title_clean):
            flash('Текст має містити принаймні 40% кирилиці', 'error')
        elif not has_minimum_words(title_clean):
            flash('Заголовок має містити щонайменше 4 слова', 'error')
        else:
            try:
                result, probability = predict_clickbait(title_clean)
            except Exception as e:
                current_app.logger.error(f"[Error] Класифікація не вдалася: {e}")
                flash("Сталася помилка під час обробки заголовка.", "error")

            try:
                conn = get_connection(DB_CONFIG['database'])
                conn.autocommit = True
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT 1 FROM classification_results
                    WHERE user_login = %s AND title = %s
                    """,
                    (session['login'], title_raw)
                )
                exists = cur.fetchone()

                if not exists:
                    cur.execute(
                        """
                        INSERT INTO classification_results
                            (user_login, title, is_clickbait, probability)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (session['login'], title_raw, result, probability)
                    )

                cur.close()
                conn.close()
            except Exception as e:
                current_app.logger.error(f"[Error] Не вдалося зберегти результат: {e}")

    return render_template(
        'index.html',
        title=title_raw,
        result=result,
        score=probability
    )
