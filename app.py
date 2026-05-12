from flask import Flask
from controllers import routes
from config import db_url

app = Flask(__name__)

routes.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)