DIR_NAME=$(basename "$PWD")

tmux kill-session -t $DIR_NAME
kill -9 $(lsof -t -i:5000)
