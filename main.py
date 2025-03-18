from flask import Flask, request, send_from_directory, render_template_string
import os
import socket
import tkinter as tk
from tkinter import messagebox
from threading import Thread

app = Flask(__name__)
UPLOAD_FOLDER = 'shared_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    files = [(f, round(os.path.getsize(os.path.join(UPLOAD_FOLDER, f)) / 1024, 2)) for f in os.listdir(UPLOAD_FOLDER)]
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
      <title>📂 File Share</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background-color: #f9f9f9; color: #333; }
        .container { max-width: 800px; margin: auto; padding: 20px; }
        h1 { text-align: center; margin-bottom: 10px; }
        form { display: flex; flex-direction: column; align-items: center; margin-bottom: 30px; }
        input[type=file] { margin: 15px 0; }
        input[type=submit] { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
        input[type=submit]:hover { background-color: #45a049; }
        #progressBar { width: 100%; background-color: #ddd; border-radius: 20px; overflow: hidden; margin-top: 10px; }
        #progressBar div { height: 20px; width: 0; background-color: #4CAF50; text-align: center; color: white; line-height: 20px; transition: width 0.4s ease; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #4CAF50; color: white; }
        tr:hover { background-color: #f1f1f1; }
        a { color: #4CAF50; text-decoration: none; }
        a:hover { text-decoration: underline; }
        @media(max-width:600px){
          table, th, td { font-size: 14px; }
          input[type=submit] { width: 80%; }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>📤 Upload Files</h1>
        <form id="uploadForm" method="post" enctype="multipart/form-data">
          <input type="file" name="files" multiple required>
          <input type="submit" value="Upload">
          <div id="progressBar"><div></div></div>
        </form>

        <h2>📁 Files Available:</h2>
        <table>
          <tr>
            <th>Filename</th>
            <th>Size (KB)</th>
            <th>Action</th>
          </tr>
          {% for filename, size in files %}
          <tr>
            <td>{{ filename }}</td>
            <td>{{ size }}</td>
            <td><a href="/files/{{ filename }}">Download</a></td>
          </tr>
          {% endfor %}
        </table>
      </div>

      <script>
        const form = document.getElementById('uploadForm');
        const progressBar = document.getElementById('progressBar').firstElementChild;

        form.addEventListener('submit', function(e) {
          e.preventDefault();
          const files = form.querySelector('input[type="file"]').files;
          const formData = new FormData();
          for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
          }

          const xhr = new XMLHttpRequest();
          xhr.open('POST', '/upload', true);

          xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
              const percentComplete = (e.loaded / e.total) * 100;
              progressBar.style.width = percentComplete + '%';
              progressBar.textContent = Math.floor(percentComplete) + '%';
            }
          };

          xhr.onload = function() {
            if (xhr.status === 200) {
              location.reload();
            } else {
              alert('Upload failed!');
            }
          };

          xhr.send(formData);
        });
      </script>
    </body>
    </html>
    ''', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    for file in files:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return 'Upload successful!'

@app.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def show_ip_dialog():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Server Running", f"🚀 File Server is Running!\n\nAccess URL:\nhttp://{ip_address}:5000/")
    root.destroy()

if __name__ == '__main__':
    Thread(target=show_ip_dialog).start()
    app.run(host='0.0.0.0', port=5500)
