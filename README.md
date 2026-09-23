# kindle-dashboard

# 📖 Dashboard Kindle Basic Edition
Um dashboard digital otimizado para a tela E-ink da **Amazon Kindle Basic Edition (11ª geração)**. Exibe relógio, data, clima em tempo real e status de serviços do homelab, com atualização automática a cada minuto via API HTTP.


## ✨ Características
- 🕒 **Relógio & Data**: Formato nativo em português (`Segunda-feira, 15 de Março`)
- 🌤️ **Clima em tempo real**: Consulta para São Paulo (-23.649, -46.852) via API Open-Meteo com cache de 15 min
- 🔌 **Monitoramento de serviços**: Verifica disponibilidade do Pi-Hole e Homelab local via endpoints HTTP
- 🔋 **Leitura da bateria**: Captura o parâmetro `?battery=XX` enviado pelo app Kindle e exibe no dashboard
- 📱 **Formato E-ink nativo**: Imagem monocromática 8-bit (`L`) em orientação paisagem (1448×1072)
- ⏱️ **Atualização síncrona**: Loop alinhado ao início de cada minuto para evitar janelas de atualização fora da hora
- 🚫 **Cache desativado**: Headers `no-store` e troca atômica de arquivos garantem sempre uma imagem atualizada


## 🛠 Instalação e Execução
1. Clone o repositório:
```sh
   git clone https://github.com/<seu-usuario>/dashboard_kindle.git
   cd dashboard_kindle
```
2. Instale Docker e Docker Compose (v2+).
3. Rode o serviço com compose:
```sh
   docker compose up --build
```
4. No app Kindle, configure uma **URL de leitura** (ou use um app que suporte URL fixa):
```
   http://<IP_DO_CONTÊNER>:8081/kindle-dashboard.png?battery=XX
```
> `XX` deve ser o valor atual da bateria do Kindle. O servidor captará esse valor e gravará no disco para exibir no próximo frame.
## 🧠 Como Funciona
| Componente | Responsabilidade |
|------------|------------------|
| `dashboard_kindle.py` | Gera a imagem em modo `"L"` (8-bit), consulta APIs, desenha texto/elementos e salva em `/output/kindle-dashboard.png` |
| `server.py` | HTTP server leve que serve o arquivo, processa o parâmetro `?battery=XX`, bloqueia cache e retorna a imagem |
| `Dockerfile` | Base `python:3.11-slim`, instala dependências (`pillow`, `requests`) e configura executável composto |
| `docker-compose.yml` | Orquestra o serviço, expõe o porto 8081 (mapeado para 8080 internamente), define volume persistente e timezone |
| dashboard.sh | Script para capturar as imagens e informações do servidor HTTP e exibi-las na tela do Kindle. Além de limitar algumas funcionalidade de exibição da tela inicial do aparelho (Framework Java), suspensão automática e proteção de tela. |
| dashboard.conf | Arquivo para executar o dashboard.sh sempre quando o Kindle for iniciado. Sempre que precisar para o script para qualquer finalidade, plugue o Kindle no PC ou laptop, e crie um arquivo em branco chamado STOP_DASHBOARD. |



## ⚙️ Customização Rápida
- **Mudar coordenadas do clima**: Edite `lat` e `lon` em `dashboard_kindle.py`
- **Adicionar/remover serviços**: Modifique a lista `targets` na função `check_service_status()`
- **Fontes customizadas**: Atualize os caminhos em `FONT_PATH_BOLD` / `FONT_PATH_REGULAR` (fontes DejaVu são incluídas pela imagem Docker)
- **Frequência de atualização**: Ajuste a variável `sleep_seconds` ou o loop no `main()`


## 📦 Requisitos
- Python 3.11+
- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0
- Fontes DejaVu Sans (incluídas automaticamente na imagem Docker)
- Kindle com Jailbreak e SSH (Esta etapa depende muito da versão do firmware ou modelo do Kindle)

## 📜 Licença
Este projeto é distribuído sob a [Licência MIT](https://opensource.org/licenses/MIT).
