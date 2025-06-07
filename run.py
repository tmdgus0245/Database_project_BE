from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="172.21.81.147", port=5000)
