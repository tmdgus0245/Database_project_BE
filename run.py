from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="172.21.81.205", port=5000)
