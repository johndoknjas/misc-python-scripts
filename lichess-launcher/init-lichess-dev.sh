#!/bin/bash
LILA_DIR="/home/johndoknjas/lichess/take-3/lila"
LILA_WS_DIR="/home/johndoknjas/lichess/take-3/lila-ws"
tmux new-session -d -s my_session "cd '$LILA_DIR'; bash"
tmux setw remain-on-exit on
tmux split-window -h "cd '$LILA_DIR'; bash"
tmux split-window -v "cd '$LILA_WS_DIR'; bash"
tmux select-pane -t 0
tmux split-window -v "cd '$LILA_DIR'; bash"
tmux -2 attach-session -d