import os
import io
import json
from flask import Flask, jsonify, request, send_from_directory, send_file

# Определяем текущую папку, где лежит main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# Встроенная SVG-схема квартиры
FLOOR_PLAN_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<rect width='100' height='100' fill='%231e293b'/>"
    "<rect x='10' y='10' width='80' height='80' fill='none' stroke='%2338bdf8' stroke-width='1.5'/>"
    "<line x1='50' y1='10' x2='50' y2='90' stroke='%2338bdf8' stroke-width='1.5'/>"
    "<line x1='10' y1='50' x2='90' y2='50' stroke='%2338bdf8' stroke-width='1.5'/>"
    "<text x='25' y='30' font-family='sans-serif' font-size='6' fill='%2394a3b8' text-anchor='middle'>Гостиная</text>"
    "<text x='75' y='30' font-family='sans-serif' font-size='6' fill='%2394a3b8' text-anchor='middle'>Кухня</text>"
    "<text x='25' y='75' font-family='sans-serif' font-size='6' fill='%2394a3b8' text-anchor='middle'>Спальня</text>"
    "<text x='75' y='75' font-family='sans-serif' font-size='6' fill='%2394a3b8' text-anchor='middle'>Санузел</text>"
    "</svg>"
)

# База данных квартир
APARTMENTS_DB = {
    "101": {
        "apartment_id": "101",
        "plan_url": FLOOR_PLAN_SVG,
        "sensors": [
            {"id": "s1", "name": "Температура", "type": "temperature", "x": 25, "y": 30, "value": 22.4, "unit": "°C"},
            {"id": "s2", "name": "Влажность", "type": "humidity", "x": 75, "y": 30, "value": 48, "unit": "%"},
            {"id": "s3", "name": "Протечка", "type": "leak", "x": 75, "y": 75, "value": "Норма", "unit": ""},
            {"id": "s4", "name": "Дым", "type": "smoke", "x": 25, "y": 75, "value": "ОК", "unit": ""},
            {"id": "s5", "name": "Энергия", "type": "meter", "x": 75, "y": 80, "value": 112, "unit": "кВт"}
        ],
        "forecast": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [120, 115, 140, 130, 160, 210, 195]
        }
    },
    "102": {
        "apartment_id": "102",
        "plan_url": FLOOR_PLAN_SVG,
        "sensors": [
            {"id": "s10", "name": "Температура", "type": "temperature", "x": 25, "y": 75, "value": 20.1, "unit": "°C"},
            {"id": "s11", "name": "Протечка", "type": "leak", "x": 75, "y": 30, "value": "АЛАРМ", "unit": "!"}
        ],
        "forecast": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [90, 85, 95, 100, 110, 130, 125]
        }
    }
}

# --- МАРШРУТИЗАЦИЯ ФАЙЛОВ ИНТЕРФЕЙСА ---

@app.route('/')
def serve_index():
    """Отдает главную страницу сайта"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Отдает css, js и картинки из той же папки"""
    return send_from_directory(BASE_DIR, filename)

# --- API ДЛЯ ЦИФРОВОГО ДВОЙНИКА ---

@app.route('/api/apartment', methods=['GET'])
def api_apartment():
    apt_id = request.args.get('id', '')
    if not apt_id:
        return jsonify({"error": "Введите ID квартиры"}), 400
    if apt_id not in APARTMENTS_DB:
        return jsonify({"error": f"Квартира №{apt_id} не найдена (попробуйте 101)"}), 404
    
    return jsonify(APARTMENTS_DB[apt_id])

@app.route('/api/apartment/report', methods=['GET'])
def api_report():
    apt_id = request.args.get('id', '')
    if not apt_id or apt_id not in APARTMENTS_DB:
        return jsonify({"error": "Неверный ID"}), 400

    apt_data = APARTMENTS_DB[apt_id]
    
    lines = [
        "=== ОТЧЕТ ЦИФРОВОГО ДВОЙНИКА ===",
        f"Объект: Квартира №{apt_id}",
        "Проект: Конкурс «Молодые строители России»",
        "-" * 30,
        "ДАТЧИКИ ТЕЛЕМЕТРИИ:"
    ]
    for s in apt_data['sensors']:
        lines.append(f" - {s['name']}: {s['value']} {s['unit']}")
    
    total = sum(apt_data['forecast']['values'])
    lines.append("-" * 30)
    lines.append(f"Прогноз расходов: {total} ₽")
    lines.append("Энергоэффективность: A+ (Оптимально)")

    mem = io.BytesIO()
    mem.write("\n".join(lines).encode('utf-8'))
    mem.seek(0)
    
    return send_file(
        mem,
        mimetype='text/plain',
        as_attachment=True,
        download_name=f"report_apt_{apt_id}.txt"
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
