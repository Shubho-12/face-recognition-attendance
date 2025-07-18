from app import create_app

app = create_app()

if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # 🔐 Set your Flask secret key here
    app.run(debug=True)
