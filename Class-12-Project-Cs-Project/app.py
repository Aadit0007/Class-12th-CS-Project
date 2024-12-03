#import Modules
from flask import Flask, render_template, request, redirect, url_for, session
import os
from collections import Counter
import csv
import re
#Set Flask App
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key for session management

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def loader():
    return render_template('loader.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload_text_file', methods=['POST'])
def upload_text_file():
    # Check if the file is in the request
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    # Check if a file was selected
    if file.filename == '':
        return 'No selected file'
    
    # Save the uploaded file to the specified folder
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    session['uploaded_file'] = file.filename  # Store the file name in the session
    
    return redirect(url_for('index'))

@app.route('/query/<query_type>', methods=['POST'])
def query_text(query_type):
    # Check if a file has been uploaded
    if 'uploaded_file' not in session:
        return redirect(url_for('index'))

    # Get the file path from the session
    uploaded_file = session['uploaded_file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)

    try:
        # Open the uploaded file and read its content
        with open(filepath, 'r') as f:
            content = f.read()

        # Perform the appropriate query based on the query_type
        if query_type == 'word_count':
            result = len(content.split())
        elif query_type == 'letter_count':
            result = sum(c.isalpha() for c in content)
        elif query_type == 'digit_count':
            result = sum(c.isdigit() for c in content)
        elif query_type == 'sentence_count':
            result = len(re.findall(r'[.!?]', content))
        elif query_type == 'paragraph_count':
            result = content.count('\n\n') + 1
        elif query_type == 'longest_word':
            words = content.split()
            result = max(words, key=len) if words else ''
        elif query_type == 'average_word_length':
            words = content.split()
            result = sum(len(word) for word in words) / len(words) if words else 0
        elif query_type == 'most_common_word':
            words = content.split()
            result = Counter(words).most_common(1)[0] if words else ('', 0)
        elif query_type == 'file_size':
            result = os.path.getsize(filepath) / 1024  # Size in KB
        else:
            result = 'Invalid query type'

        # Render the result page with the query result
        return render_template('result.html', query_type=query_type, result=result)

    except Exception as e:
        # Handle any errors that may occur during file processing
        return f"Error processing file: {str(e)}"

@app.route('/binary')
def indexBinary():
    return render_template('indexBinary.html')

@app.route('/upload_binary_file', methods=['POST'])
def upload_binary_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    # Save the uploaded binary file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Store the filename in the session
    session['uploaded_binary_file'] = file.filename
    
    return redirect(url_for('indexBinary'))

@app.route('/query_binary/<query_type>', methods=['POST'])
def query_binary(query_type):
    if 'uploaded_binary_file' not in session:
        return redirect(url_for('indexBinary'))

    uploaded_file = session['uploaded_binary_file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)

    with open(filepath, 'rb') as f:
        content = f.read()

    if query_type == 'file_size':
        result = os.path.getsize(filepath) / 1024  # size in KB
    elif query_type == 'read_content':
        result = content  # This may be too large for display, consider limiting
    elif query_type == 'most_common_word':
        text_content = content.decode(errors='ignore')  # Decode binary content
        words = text_content.split()
        result = Counter(words).most_common(1)[0] if words else ('', 0)
    elif query_type == 'letter_count':
        text_content = content.decode(errors='ignore')
        result = sum(c.isalpha() for c in text_content)
    elif query_type == 'digit_count':
        text_content = content.decode(errors='ignore')
        result = sum(c.isdigit() for c in text_content)
    elif query_type == 'word_count':
        text_content = content.decode(errors='ignore')
        result = len(text_content.split())
    elif query_type == 'longest_word':
        text_content = content.decode(errors='ignore')
        words = text_content.split()
        result = max(words, key=len) if words else ''

    return render_template('resultB.html', query_type=query_type, result=result)

@app.route('/csv')
def indexCSV():
    return render_template('indexCSV.html')

@app.route('/upload_csv_file', methods=['POST'])
def upload_csv_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    # Save the uploaded CSV file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Store the filename in the session
    session['uploaded_csv_file'] = file.filename
    
    return redirect(url_for('indexCSV'))

@app.route('/query_csv/<query_type>', methods=['POST'])
def query_csv(query_type):
    if 'uploaded_csv_file' not in session:
        return redirect(url_for('indexCSV'))

    uploaded_file = session['uploaded_csv_file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)

    if query_type == 'file_size':
        result = os.path.getsize(filepath) / 1024  # size in KB
    elif query_type == 'read_content':
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            content = list(reader)
        result = content  # Display all content
    elif query_type == 'number_of_records':
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            result = sum(1 for row in reader) - 1  # Subtract 1 for header
    elif query_type == 'number_of_fields':
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            result = len(header)
    elif query_type == 'number_of_words':
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            content = ' '.join([' '.join(row) for row in reader])
        result = len(content.split())
    elif query_type == 'number_of_letters':
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            content = ' '.join([' '.join(row) for row in reader])
        result = sum(c.isalpha() for c in content)
    elif query_type == 'most_common_word':
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            content = ' '.join([' '.join(row) for row in reader])
        words = content.split()
        result = Counter(words).most_common(1)[0] if words else ('', 0)

    return render_template('resultCSV.html', query_type=query_type, result=result)

if __name__ == '__main__':
    app.run(debug=True)
