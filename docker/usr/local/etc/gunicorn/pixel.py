# Gunicorn-django settings
bind = ['unix:/app/pixel/run/gunicorn.sock']
graceful_timeout = 90
loglevel = 'error'
name = 'pixel'
python_path = '/app/pixel'
timeout = 90
workers = 3
