from src.models.server import Server

server = Server(
    host = "172.16.1.163",
    qnt_users = 10
)

server.start()