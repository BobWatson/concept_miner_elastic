from web.web import app as web_app
import os


def main():
    os.environ["FLASK_ENV"] = "development"
    web_app.run(host="0.0.0.0", debug=True, threaded=True)


if __name__ == "__main__":
    main()
