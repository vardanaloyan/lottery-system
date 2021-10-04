# Gunicorn config variables
loglevel = "info"
errorlog = "-"
accesslog = "stdout"
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
timeout = 120
keepalive = 5
threads = 3
