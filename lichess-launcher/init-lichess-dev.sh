#!/bin/bash
LILA_DIR="/home/johndoknjas/lichess/take-3/lila"
LILA_WS_DIR="/home/johndoknjas/lichess/take-3/lila-ws"
tmux new-session -d -s my_session "cd '$LILA_DIR'; echo 'Command: redis-server'; bash"
tmux setw remain-on-exit on
tmux split-window -h "cd '$LILA_DIR'; echo 'Command: mongod'; bash"
tmux split-window -v "cd '$LILA_WS_DIR'; echo 'Command: sbt run -Dcsrf.origin=http://localhost:9663'; bash"
tmux select-pane -t 0
tmux split-window -v "cd '$LILA_DIR'; echo 'Command: ui/build -w'; bash"
tmux -2 attach-session -d