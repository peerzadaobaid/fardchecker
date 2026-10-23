# Read automatically by gunicorn on Render, whatever the start command says.
timeout = 180          # document reading can take longer than the 30 s default
workers = 1            # one process keeps memory inside Render's free 512 MB
threads = 2
max_requests = 40      # recycle the worker now and then to release memory
max_requests_jitter = 10
