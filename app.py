from flask import Flask, render_template, url_for
import datetime
import pytz

app = Flask(__name__)
@app.route('/')
def index():
    name = "Cole"
    currHour = datetime.datetime.now(pytz.timezone('EST')).hour
    if currHour < 12:
        welcome = "Good Morning, " + name + "!"
    elif currHour < 18: 
        welcome = "Good Afternoon, " + name + "!"
    elif currHour < 21:
        welcome = "Good Evening, " + name + "!"
    else:
        welcome = "Good Night, " + name + "!"
    
    return render_template('index.html', welcome=welcome)

if __name__ == '__main__':
    app.run(debug=False)