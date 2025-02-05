#!/bin/bash
LILA_DIR="/home/johndoknjas/lichess/take-3/lila"
LILA_WS_DIR="/home/johndoknjas/lichess/take-3/lila-ws"
tmux new-session -d -s my_session "cd '$LILA_DIR' && ./lila.sh; bash"
tmux setw remain-on-exit on
tmux split-window -h "cd '$LILA_DIR' && ui/build -w; bash"
tmux split-window -v "cd '$LILA_DIR' && killall redis-server && sleep 1; redis-server; bash"
tmux select-pane -t 0
tmux split-window -v "cd '$LILA_DIR' && mongod; bash"
tmux split-window -h "cd '$LILA_WS_DIR' && sbt run -Dcsrf.origin=http://localhost:9663; bash"
tmux swap-pane -s 1 -t 2
tmux -2 attach-session -d