#!/bin/sh
source venv_vlab/bin/activate

while true; do
  flask deploy
  if [[ "$?" == "0" ]]; then 
    break
  fi

  echo Deploy command failed, retrying in 5 secs ...
  sleep 5
done

exec gunicorn -b :5000 --access-logfile - --error-logfile - nomads.server:app
#exec gunicorn -b :5000 --access-logfile - --error-logfile - nomads.server:app
#flask run --host=0.0.0.0 --port=5000