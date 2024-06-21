import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your_secret_key_here'  # Cambia esto por una clave segura en un entorno de producción

# Función para verificar las credenciales del usuario (solo como ejemplo, deberías usar una base de datos real)
def authenticate(username, password):
    return username == 'admin' and password == 'admin'  # Cambia esto por una verificación real de las credenciales

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

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
    if 'username' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)  # Redondear a dos decimales
    return render_template('file_details.html', filename=filename, file_size_mb=file_size_mb)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

