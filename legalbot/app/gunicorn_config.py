bind = ":8000"
module = "config.wsgi:application"

workers = 4  # Adjust based on your server's resources
worker_connections = 1000
threads = 4

