#!/bin/sh

SERVER_URL="http://<SEU_IP_DO_SERVIDOR>:8081/kindle-dashboard.png"
IMAGE_PATH="/tmp/dashboard.png"
COUNT=0
REFRESH_EVERY=10

# 1. Desativa proteções de tela nativas e suspensão automática
lipc-set-prop -i com.lab126.powerd preventScreenSaver 1 2>/dev/null
lipc-set-prop -i com.lab126.powerd deferSuspend 1 2>/dev/null
lipc-set-prop -i com.lab126.powerd flWorkflow 0 2>/dev/null

# 2. Para o Framework Java (remove a tela inicial da Amazon)
stop framework 2>/dev/null || /etc/init.d/framework stop 2>/dev/null

iwconfig wlan0 power off 2>/dev/null

ntpdate -u pool.ntp.br 2>/dev/null || ntpdate -u time.google.com 2>/dev/null &

# 3. Dá 2 segundos para o display liberar e limpa a tela
sleep 2
eips -c
usleep 250000

while true; do
    # Garante periodicamente que a proteção de tela não seja reativada
    lipc-set-prop -i com.lab126.powerd preventScreenSaver 1 2>/dev/null

    # Coleta bateria
    BATT=$(lipc-get-prop -i com.lab126.powerd battLevel 2>/dev/null)
    if [ -z "$BATT" ]; then
        BATT=$(cat /sys/devices/system/yoshi_battery/yoshi_battery0/battery_capacity 2>/dev/null || cat /sys/class/power_supply/battery/capacity 2>/dev/null)
    fi

    # Baixa e estampa no e-ink
    curl -s -f -o "$IMAGE_PATH" "${SERVER_URL}?battery=${BATT:-100}"

    if [ $? -eq 0 ]; then
        if [ $((COUNT % REFRESH_EVERY)) -eq 0 ]; then
            eips -c
            usleep 250000
        fi
        eips -g "$IMAGE_PATH"
        COUNT=$((COUNT + 1))
    fi

    # Sincroniza virada do minuto
    CURRENT_SEC=$(date +%S | sed 's/^0*//')
    [ -z "$CURRENT_SEC" ] && CURRENT_SEC=0
    SLEEP_TIME=$((61 - CURRENT_SEC))

    sleep $SLEEP_TIME
done
