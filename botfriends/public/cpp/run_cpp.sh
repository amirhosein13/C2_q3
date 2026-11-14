#!/bin/bash

problem="botfriends"
memory=524288  # 512MB
stack_size=2097152  # 2GB

ulimit -v "${memory}"
ulimit -s "${stack_size}"
"./${problem}"
