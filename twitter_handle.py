__author__ = 'trishia'
from flask import Flask, render_template, request

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('test.html')

@app.route('/hello', methods=['POST'])
def hello():
    twitter_handle = request.form['twitter_handle']
    return 'Hello %s have fun learning python <br/> <a href="/">Back Home</a>' % (twitter_handle)

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 80, threaded=True)