from flask import Flask
app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def hello():

    oneCloudHub = '<div style = "position:fixed; left:80px; top:20px;">' \
                  '<img src="https://www.1cloudhub.com/wp-content/uploads/2018/08/1chlogo.png" width="150" height="50">' \
                  '</div>'
    hello = '<div style = "position:fixed; text-align:center; top:28px; width: 100%; height: 10px; font-size: 30px;">' \
            '<p>Hello World!!!</p>' \
            '</div>'
    microsoft = '<div style = "position:fixed; right:80px; top:28px;">' \
                '<img src="https://img-prod-cms-rt-microsoft-com.akamaized.net' \
                '/cms/api/am/imageFileData/RE1Mu3b?ver=5c31" width="170" height="30"</div>'
    return oneCloudHub + hello + microsoft


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
