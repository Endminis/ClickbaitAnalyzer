from flask import Blueprint, request, jsonify
from predict import predict_clickbait
from utils.text_utils import clean_text, contains_cyrillic, has_minimum_words
from db import get_connection
from config import DB_CONFIG

extension_api = Blueprint('extension_api', __name__, url_prefix='/extension/api')

@extension_api.route('/check', methods=['POST'])
def check_clickbait():
    payload = request.get_json(force=True)

    # Витягаємо список заголовків
    if isinstance(payload, list):
        titles = payload
    elif isinstance(payload, dict):
        if 'titles' in payload:
            titles = payload['titles']
        elif 'title' in payload:
            titles = [payload['title']]
        else:
            return jsonify({"error": "Не знайдено ключів 'title' або 'titles'"}), 400
    else:
        return jsonify({"error": "Невірний формат даних"}), 400

    results = []
    conn    = get_connection(DB_CONFIG['database'])
    cur     = conn.cursor()

    for raw in titles:
        text = str(raw).strip()

        # Валідація тексту
        if not contains_cyrillic(text) or not has_minimum_words(text):
            results.append(False)
            cur.execute(
                "INSERT INTO extension_results (title, is_clickbait, probability) "
                "VALUES (%s, %s, %s)",
                (text, False, 0.0)
            )
            continue

        # 1) Шукаємо в базі готовий результат
        cur.execute(
            "SELECT is_clickbait, probability "
            "FROM extension_results "
            "WHERE title = %s "
            "ORDER BY created_at DESC "
            "LIMIT 1",
            (text,)
        )
        row = cur.fetchone()
        if row:
            is_clickbait, probability = row
            results.append(bool(is_clickbait))
        else:
            # 2) Якщо нема — прогнозуємо й зберігаємо
            clean = clean_text(text)
            is_clickbait, probability = predict_clickbait(clean)
            results.append(bool(is_clickbait))
            cur.execute(
                "INSERT INTO extension_results (title, is_clickbait, probability) "
                "VALUES (%s, %s, %s)",
                (text, is_clickbait, probability)
            )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify(results)
