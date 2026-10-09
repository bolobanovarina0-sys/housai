import http.server
import socketserver
import json
import urllib.parse
import os
import io

PORT = int(os.environ.get("PORT", 8000))

# Встроенная SVG-схема квартиры для демонстрации (планировка с комнатами)
FLOOR_PLAN_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<rect width='100' height='100' fill='%23f1f5f9'/>"
    "<rect x='10' y='10' width='80' height='80' fill='none' stroke='%2394a3b8' stroke-width='2'/>"
    "<line x1='50' y1='10' x2='50' y2='90' stroke='%2394a3b8' stroke-width='2'/>"
    "<line x1='10' y1='50' x2='90' y2='50' stroke='%2394a3b8' stroke-width='2'/>"
    "<text x='25' y='30' font-family='sans-serif' font-size='6' fill='%2364748b' text-anchor='middle'>Гостиная</text>"
    "<text x='75' y='30' font-family='sans-serif' font-size='6' fill='%2364748b' text-anchor='middle'>Кухня</text>"
    "<text x='25' y='75' font-family='sans-serif' font-size='6' fill='%2364748b' text-anchor='middle'>Спальня</text>"
    "<text x='75' y='75' font-family='sans-serif' font-size='6' fill='%2364748b' text-anchor='middle'>Санузел</text>"
    "</svg>"
)

# База данных цифровых двойников квартир (модуль «Цифровая трансформация дома»)
APARTMENTS_DB = {
    "101": {
        "apartment_id": "101",
        "plan_url": FLOOR_PLAN_SVG,
        "sensors": [
            {"id": "s1", "name": "Температура (Гостиная)", "type": "temperature", "x": 25, "y": 30, "value": 22.4, "unit": "°C"},
            {"id": "s2", "name": "Влажность (Кухня)", "type": "humidity", "x": 75, "y": 30, "value": 48, "unit": "%"},
            {"id": "s3", "name": "Контроль протечки (Санузел)", "type": "leak", "x": 75, "y": 75, "value": "Норма", "unit": ""},
            {"id": "s4", "name": "Детектор дыма (Спальня)", "type": "smoke", "x": 25, "y": 75, "value": "ОК", "unit": ""},
            {"id": "s5", "name": "Счетчик ХВС", "type": "meter", "x": 75, "y": 80, "value": 112.4, "unit": "м³"}
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
            {"id": "s10", "name": "Температура (Спальня)", "type": "temperature", "x": 25, "y": 75, "value": 20.1, "unit": "°C"},
            {"id": "s11", "name": "Контроль протечки (Кухня)", "type": "leak", "x": 75, "y": 30, "value": "АЛАРМ", "unit": "!"}
        ],
        "forecast": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [90, 85, 95, 100, 110, 130, 125]
        }
    }
}

class DigitalTwinHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # Эндпоинт получения данных квартиры по ID
        if path == "/api/apartment":
            query = urllib.parse.parse_qs(parsed_path.query)
            apt_id = query.get("id", [""])[0]
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            if not apt_id:
                self.wfile.write(json.dumps({"error": "Параметр 'id' обязателен"}, ensure_ascii=False).encode("utf-8"))
            elif apt_id not in APARTMENTS_DB:
                self.wfile.write(json.dumps({"error": f"Квартира с ID {apt_id} не найдена"}, ensure_ascii=False).encode("utf-8"))
            else:
                self.wfile.write(json.dumps(APARTMENTS_DB[apt_id], ensure_ascii=False).encode("utf-8"))
            return

        # Эндпоинт генерации и скачивания отчета
        elif path == "/api/apartment/report":
            query = urllib.parse.parse_qs(parsed_path.query)
            apt_id = query.get("id", [""])[0]
            if not apt_id or apt_id not in APARTMENTS_DB:
                self.send_response(400)
                self.end_headers()
                return

            apt_data = APARTMENTS_DB[apt_id]
            report_lines = [
                "=== ОТЧЕТ ЦИФРОВОГО ДВОЙНИКА КВАРТИРЫ ===",
                f"Объект: Квартира №{apt_id}",
                "Проект: Всероссийский конкурс «Молодые строители России»",
                "Номинация: Цифровая трансформация дома",
                "-" * 45,
                "ТЕЛЕМЕТРИЯ ДАТЧИКОВ:",
            ]
            for s in apt_data['sensors']:
                report_lines.append(f" • {s['name']}: {s['value']} {s['unit']}")
            
            total_cost = sum(apt_data['forecast']['values'])
            report_lines.append("-" * 45)
            report_lines.append(f"Прогнозируемый расход ресурсов на неделю: {total_cost} ₽")
            report_lines.append("Статус энергоэффективности: Класс A+ (Оптимизировано)")

            content = "\n".join(report_lines)
            mem = io.BytesIO()
            mem.write(content.encode('utf-8'))
            mem.seek(0)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename=report_apartment_{apt_id}.txt")
            self.end_headers()
            self.wfile.write(mem.read())
            return

        # Обслуживание статических файлов из текущей директории
        return super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), DigitalTwinHandler) as httpd:
        print(f"Сервер цифрового двойника запущен! Откройте в браузере: http://localhost:{PORT}")
        httpd.serve_forever()