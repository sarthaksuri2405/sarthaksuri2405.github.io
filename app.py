from flask import Flask, request, render_template, send_file
import os
import shutil
import zipfile
import time
from compare_faces import compare_faces

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    status = ''  # Initialize status
    error = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file part"
        else:
            files = request.files.getlist('file')
            matches_list = []

            for file in files:
                if file.filename == '':
                    continue

                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Create the 'uploads' directory if it doesn't exist
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(file_path)
                # Update status
                status = 'Processing...'
                matches = compare_faces(file_path, app.config['DATABASE_FOLDER'], app.config['OUTPUT_FOLDER'])
                matches_list.append(matches)

            # Create zip file
            zip_file_path = os.path.join(app.config['OUTPUT_FOLDER'], 'matched_images.zip')
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for root, dirs, files in os.walk(app.config['OUTPUT_FOLDER']):
                    for file in files:
                        if file.endswith('.jpg') or file.endswith('.png'):  # Only add image files
                            zipf.write(os.path.join(root, file), file)

            # Update status
            status = 'Creating download file...'
            time.sleep(1)
            # Provide zip file as downloadable link
            return send_file(zip_file_path, as_attachment=True)
            
    return render_template('index.html', status=status, error=error)

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['DATABASE_FOLDER'] = 'database'
    app.config['OUTPUT_FOLDER'] = 'matched_images'
    app.run(debug=True)
