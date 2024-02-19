# gunicorn_conf.py

bind = "127.0.0.1:4545"

# Worker Options
# workers = cpu_count() + 1
workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = './access_log'
errorlog = './error_log'
