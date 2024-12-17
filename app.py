from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configure upload folder and allowed file types
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
def init_db():
    conn = sqlite3.connect('receipts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            amount REAL,
            date TEXT,
            description TEXT,
            uploaded_on TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def upload_receipt():
    if request.method == 'POST':
        file = request.files['file']
        amount = request.form['amount']
        date = request.form['date']
        description = request.form['description']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Save details to the database
            conn = sqlite3.connect('receipts.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO receipts (filename, amount, date, description, uploaded_on)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, amount, date, description, datetime.now()))
            conn.commit()
            conn.close()
            
            return redirect(url_for('upload_receipt'))
    
    return render_template('upload.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
