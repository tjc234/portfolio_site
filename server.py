from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bio')
def bio():
    return render_template('bio.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/checkers')
def checkers():
    return render_template('checkers.html')

if __name__ == '__main__':
    app.run(debug=True)
