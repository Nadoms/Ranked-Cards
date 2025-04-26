#!/bin/bash
DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
BOT="$DIR/bot.py"
TIMESTAMP=$(date +"%m%d-%H%M")
LOG_FILE="$DIR/logs/bot_$TIMESTAMP.log"
python3 -u "$BOT" 2>&1 | tee "$LOG_FILE"
