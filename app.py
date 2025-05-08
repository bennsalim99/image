from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove
from PIL import Image
import os
from datetime import datetime

app = Flask(__name__)

# Klasör yapılandırması
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{timestamp}.png"
    
    input_path = os.path.join(UPLOAD_FOLDER, f"input_{timestamp}.png")
    output_path = os.path.join(RESULT_FOLDER, output_filename)

    try:
        file.save(input_path)
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path)

        os.remove(input_path)  # Geçici dosyayı sil

        # JSON yanıtı döndür
        return jsonify({
            'success': True,
            'filename': output_filename,
            'message': 'Görsel başarıyla işlendi'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join('static', 'results', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Dosya bulunamadı'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)