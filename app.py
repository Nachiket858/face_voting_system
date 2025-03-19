# from flask import Flask, render_template
# from db import mongo  # Import MongoDB instance from db.py
# from routes.admin import admin_bp
# from routes.voter import voter_bp

# app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/voting_system"
# app.config["SECRET_KEY"] = "your_super_secret_key"

# mongo.init_app(app)  # Initialize MongoDB with the Flask app

# # Register Blueprints
# app.register_blueprint(admin_bp, url_prefix="/admin")
# app.register_blueprint(voter_bp, url_prefix="/voter")
# print("Under Kodeneurons, visit: https://kodeneurons.vercel.app")
# @app.route("/")
# def home():
#     return render_template("first.html")

# @app.route("/index")
# def index():
#     return render_template("index.html")


# if __name__ == "__main__":
#     app.run(debug=True)


import os
import shutil
from flask import Flask, render_template
from db import mongo  # Import MongoDB instance from db.py
from routes.admin import admin_bp
from routes.voter import voter_bp

# Function to remove __pycache__ folders
def remove_pycache():
    for root, dirs, files in os.walk("routes"):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                # print(f"Deleted: {pycache_path}")

remove_pycache()  # Call the function before starting the app

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/voting_system"
app.config["SECRET_KEY"] = "your_super_secret_key"

mongo.init_app(app)  # Initialize MongoDB with the Flask app

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(voter_bp, url_prefix="/voter")

print("Under Kodeneurons, visit: https://kodeneurons.vercel.app")

@app.route("/")
def home():
    return render_template("first.html")

@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
