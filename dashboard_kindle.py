import os
import time
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont

# Dimensões invertidas para Modo Paisagem (Kindle Basic 11ª geração: 1448x1072)
WIDTH = 1448
HEIGHT = 1072

BG_COLOR = 255  # Branco
TEXT_COLOR = 0  # Preto

FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

TIME_SIZE = 130
DATE_SIZE = 36
TEMP_SIZE = 96
SECTION_TITLE_SIZE = 38
ITEM_SIZE = 32
SMALL_TEXT_SIZE = 24

MARGIN_X = 60
MARGIN_Y = 60
COL_SPLIT_X = 720  # Ponto central divisório das colunas

_weather_cache = {"temp": None, "desc": "Carregando...", "last_fetch": 0}

DAYS_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
MONTHS_PT = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def get_weather():
    global _weather_cache
    now_ts = time.time()
    
    if now_ts - _weather_cache["last_fetch"] < 900 and _weather_cache["temp"] is not None:
        return _weather_cache
    # Configure aqui sua região
    lat = -00.000
    lon = -00.000
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
    }
    
    weather_codes = {
        0: "Céu limpo", 1: "Poucas nuvens", 2: "Parcialmente nublado", 
        3: "Nublado", 45: "Neblina", 51: "Garoa leve", 61: "Chuva leve",
        63: "Chuva moderada", 65: "Chuva forte", 80: "Pancadas de chuva", 
        95: "Tempestade"
    }
    
    try:
        r = requests.get(url, params=params, timeout=4)
        r.raise_for_status()
        data = r.json()
        _weather_cache["temp"] = round(data["current"]["temperature_2m"])
        code = data["current"]["weather_code"]
        _weather_cache["desc"] = weather_codes.get(code, "Tempo instável")
        _weather_cache["last_fetch"] = now_ts
    except Exception as e:
        print(f"Erro ao buscar clima: {e}")
        if _weather_cache["temp"] is None:
            _weather_cache["desc"] = "Sem dados"
            
    return _weather_cache


def check_service_status():
    targets = [
        ("NOME_DO_SERVIÇO", "http://<IP_DO_SEU_SERVICO>"),
        ("NOME_DO_SERVIÇO", "http://<IP_DO_SEU_SERVICO>"),
    ]
    results = []
    for name, url in targets:
        ok = False
        try:
            r = requests.get(url, timeout=2)
            ok = (r.status_code < 400)
        except Exception:
            ok = False
        results.append((name, "●" if ok else "○"))
    return results


def get_kindle_battery():
    batt_path = "/output/kindle_battery.txt"
    if os.path.exists(batt_path):
        try:
            with open(batt_path, "r") as f:
                val = f.read().strip()
                if val:
                    return f"{val}%"
        except Exception:
            pass
    return "--%"


def load_font(font_path, size, fallback_path=None):
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        if fallback_path:
            try:
                return ImageFont.truetype(fallback_path, size)
            except OSError:
                pass
        return ImageFont.load_default()


def render_dashboard():
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = f"{DAYS_PT[now.weekday()]}, {now.day} de {MONTHS_PT[now.month]}"

    weather = get_weather()
    services = check_service_status()
    battery_str = f"Bateria: {get_kindle_battery()}"

    # Imagem 8-bit em tons de cinza nativa
    img = Image.new("L", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    time_font = load_font(FONT_PATH_BOLD, TIME_SIZE, FONT_PATH_REGULAR)
    date_font = load_font(FONT_PATH_BOLD, DATE_SIZE, FONT_PATH_REGULAR)
    temp_font = load_font(FONT_PATH_BOLD, TEMP_SIZE, FONT_PATH_REGULAR)
    title_font = load_font(FONT_PATH_BOLD, SECTION_TITLE_SIZE, FONT_PATH_REGULAR)
    item_font = load_font(FONT_PATH_REGULAR, ITEM_SIZE, FONT_PATH_REGULAR)
    small_font = load_font(FONT_PATH_REGULAR, SMALL_TEXT_SIZE, FONT_PATH_REGULAR)

    # ===== COLUNA ESQUERDA: RELÓGIO & CLIMA =====
    col1_x = MARGIN_X
    col1_y = MARGIN_Y

    # Hora e Data
    draw.text((col1_x, col1_y), time_str, font=time_font, fill=TEXT_COLOR)
    col1_y += TIME_SIZE + 10

    draw.text((col1_x, col1_y), date_str, font=date_font, fill=TEXT_COLOR)
    col1_y += DATE_SIZE + 40

    draw.line([(col1_x, col1_y), (COL_SPLIT_X - 50, col1_y)], fill=TEXT_COLOR, width=3)
    col1_y += 45

    # Bloco de Clima
    box_w = (COL_SPLIT_X - 50) - col1_x
    box_h = 240
    draw.rectangle([col1_x, col1_y, col1_x + box_w, col1_y + box_h], outline=TEXT_COLOR, width=2)

    temp_text = f"{weather['temp']}°C" if weather['temp'] is not None else "--°C"
    draw.text((col1_x + 30, col1_y + 25), temp_text, font=temp_font, fill=TEXT_COLOR)
    draw.text((col1_x + 30, col1_y + 140), weather['desc'], font=item_font, fill=TEXT_COLOR)

    # ===== DIVISÓRIA VERTICAL =====
    draw.line([(COL_SPLIT_X, MARGIN_Y), (COL_SPLIT_X, HEIGHT - MARGIN_Y - 40)], fill=TEXT_COLOR, width=3)

    # ===== COLUNA DIREITA: SERVIÇOS =====
    col2_x = COL_SPLIT_X + 50
    col2_y = MARGIN_Y + 15

    draw.text((col2_x, col2_y), "Status dos Serviços", font=title_font, fill=TEXT_COLOR)
    col2_y += SECTION_TITLE_SIZE + 20
    draw.line([(col2_x, col2_y), (WIDTH - MARGIN_X, col2_y)], fill=TEXT_COLOR, width=2)
    col2_y += 35

    for name, status in services:
        draw.text((col2_x, col2_y), f"  {status}   {name}", font=item_font, fill=TEXT_COLOR)
        col2_y += ITEM_SIZE + 25

    # ===== RODAPÉ =====
    update_text = f"Atualizado em: {now.strftime('%H:%M:%S')}"
    draw.text((MARGIN_X, HEIGHT - 50), update_text, font=small_font, fill=TEXT_COLOR)
    draw.text((WIDTH - MARGIN_X - 220, HEIGHT - 50), battery_str, font=small_font, fill=TEXT_COLOR)

    # Escrita atômica em modo 'L' (8-bit grayscale) exigido pelo eips
    img_final = img.rotate(90, expand=True)

    # Escrita atômica em modo 'L' (8-bit grayscale)
    os.makedirs("/output", exist_ok=True)
    temp_path = "/output/kindle-dashboard.png.tmp"
    final_path = "/output/kindle-dashboard.png"

    img_final.save(temp_path, format="PNG")
    os.replace(temp_path, final_path)


def main():
    while True:
        try:
            render_dashboard()
        except Exception as e:
            print(f"Erro na renderização: {e}")

        # Sincroniza o loop no topo de cada minuto (:00)
        now = datetime.datetime.now()
        sleep_seconds = 60 - now.second
        time.sleep(sleep_seconds if sleep_seconds > 0 else 60)


if __name__ == "__main__":
    main()
