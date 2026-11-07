# FARD CHECKER VERSION 1.9.12
# Read automatically by gunicorn on Render, whatever the start command says.
timeout = 180          # document reading can take longer than the 30 s default
workers = 1            # one process keeps memory inside Render's free 512 MB
threads = 2
max_requests = 300     # backstop only — from v1.9.12 the app itself restarts the worker after every 20 analyses (ANALYSES_PER_WORKER)
max_requests_jitter = 5
graceful_timeout = 60  # a worker being replaced finishes its analysis / online save first
