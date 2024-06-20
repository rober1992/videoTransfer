import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Simulate upload progress (this can be replaced with a real implementation)
        for i in range(101):
            update_progress(i)
        
        return redirect(url_for('file_details', filename=filename))

def update_progress(percentage):
    with app.app_context():
        from flask_socketio import SocketIO, emit
        socketio = SocketIO(message_queue='redis://')
        socketio.emit('update_progress', {'percentage': percentage}, namespace='/progress')

@app.route('/file/<filename>')
def file_details(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)  # Redondear a dos decimales
    return render_template('file_details.html', filename=filename, file_size_mb=file_size_mb)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
