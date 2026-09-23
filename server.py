import os
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler

class BatteryAwareNoCacheHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        # Captura ?battery=XX do Kindle e armazena em disco
        if "battery" in qs:
            batt_val = qs["battery"][0]
            try:
                with open("/output/kindle_battery.txt", "w") as f:
                    f.write(batt_val)
            except Exception as e:
                print(f"Erro ao salvar bateria: {e}")

        # Remove query parameters para que a imagem seja servida normalmente
        self.path = parsed.path
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

if __name__ == "__main__":
    os.chdir("/output")
    server = HTTPServer(("0.0.0.0", 8080), BatteryAwareNoCacheHandler)
    server.serve_forever()