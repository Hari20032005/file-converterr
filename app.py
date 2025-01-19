from flask import Flask, render_template, request, send_file, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    convert_to = request.form.get('convert_to', 'png')
    
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        # Read the uploaded image
        image = Image.open(file)
        
        # Prepare the converted image
        converted_image = io.BytesIO()
        
        # Convert to RGB if necessary (in case of PNG with transparency)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        
        # Save with the new format
        image.save(converted_image, format=convert_to.upper())
        converted_image.seek(0)
        
        # Generate converted filename
        original_filename = secure_filename(file.filename)
        filename_without_ext = os.path.splitext(original_filename)[0]
        converted_filename = f"{filename_without_ext}.{convert_to}"
        
        # Save the converted file temporarily
        converted_path = os.path.join(app.config['UPLOAD_FOLDER'], converted_filename)
        with open(converted_path, 'wb') as f:
            f.write(converted_image.getvalue())
        
        return render_template('result.html', converted_file=converted_filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)