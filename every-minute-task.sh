pa_update_scheduled_task.py $1 -m $(date -d"$(date) + 1 minute" +"%M") -p
source /home/Yerdos/project_aya/.venv/bin/activate && python /home/Yerdos/project_aya/project_aya/apps/main/send_to_bot.py