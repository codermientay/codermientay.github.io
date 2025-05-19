import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from video import video_transfer
from stylize import stylize

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Đảm bảo các thư mục tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Map style name to model path
STYLE_MAP = {
    "starry_night": "transforms/starry.pth",
    "mosaic": "transforms/mosaic.pth",
    "tokyo_ghoul": "transforms/tokyo_ghoul.pth",
    "udnie": "transforms/udnie.pth",
    "wave": "transforms/wave.pth",
    "bayanihan": "transforms/bayanihan.pth",
    "lazy": "transforms/lazy.pth"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files or 'style' not in request.form:
        return jsonify({'error': 'Thiếu dữ liệu'}), 400

    file = request.files['image']
    style = request.form['style']
    if style not in STYLE_MAP:
        return jsonify({'error': 'Style không hợp lệ'}), 400

    # Đảm bảo thư mục tồn tại
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

    # Lưu ảnh gốc vào uploads/
    input_img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.jpg')
    file.save(input_img_path)

    # Lưu ảnh kết quả vào processed/
    output_img_path = os.path.join(app.config['PROCESSED_FOLDER'], 'output.jpg')
    stylize(STYLE_MAP[style], input_img_path, output_img_path)

    if not os.path.exists(output_img_path):
        return jsonify({'error': 'Không tìm thấy ảnh kết quả'}), 500
    return send_file(output_img_path, mimetype='image/jpeg')

@app.route('/api/process-video', methods=['POST'])
def process_video():
    if 'video' not in request.files or 'style' not in request.form:
        return jsonify({'error': 'Thiếu dữ liệu'}), 400

    file = request.files['video']
    style = request.form['style']
    if style not in STYLE_MAP:
        return jsonify({'error': 'Style không hợp lệ'}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    # Đặt lại tên cho video đầu vào/đầu ra
    video_input = upload_path
    video_output = os.path.join(app.config['PROCESSED_FOLDER'], 'output.mp4')

    # Chạy style transfer cho video
    video_transfer(video_input, STYLE_MAP[style])

    # Đường dẫn file kết quả thực tế (ví dụ: output.mp4 ở thư mục gốc)
    default_output = 'output.mp4'
    video_output = os.path.join(app.config['PROCESSED_FOLDER'], 'output.mp4')

    if os.path.exists(default_output):
        os.replace(default_output, video_output)
    else:
        return jsonify({'error': 'Không tìm thấy file video kết quả'}), 500

    return send_file(video_output, mimetype='video/mp4')

# Route trả về ảnh placeholder (demo)
@app.route('/api/placeholder/<int:w>/<int:h>')
def placeholder(w, h):
    from PIL import Image, ImageDraw
    import io
    img = Image.new('RGB', (w, h), color=(200, 200, 200))
    d = ImageDraw.Draw(img)
    d.text((10, h//2-10), f"{w}x{h}", fill=(100, 100, 100))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)