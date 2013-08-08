from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
        return 'Hello World!'

@app.route('/heatmap/')
def heat_map(name=None):
    return render_template('heatmap.html', name=name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
#shauns comment


