from flask import Flask
app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def hello():
    hello = '<div style = "position:fixed; text-align:center; top:10px; width: 100%; height: 10px; font-size: 30px;">' \
            '<p>Hello World!!</p></div>'
    return hello


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
