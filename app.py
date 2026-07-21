import os
import io
import math
import zipfile
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageFilter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

HERE = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(HERE, 'icone.jpeg')

icon_cache = None

def get_icon():
    global icon_cache
    if icon_cache is None:
        raw = Image.open(ICON_PATH).convert('RGBA')
        gray = raw.convert('L')
        alpha = gray.point(lambda x: 0 if x < 40 else min(255, int((x - 40) * (255.0 / 215.0))))
        alpha = alpha.filter(ImageFilter.GaussianBlur(radius=3))
        raw.putalpha(alpha)
        icon_cache = raw
    return icon_cache.copy()

def apply_watermark(uploaded_image, opacity=0.45, size_percent=0.20):
    img = uploaded_image.convert('RGBA')
    icon = get_icon()

    iw, ih = img.size

    wm_w = int(iw * size_percent)
    wm_h = int(wm_w * icon.height / icon.width)
    if wm_w > icon.width:
        wm_w = icon.width
        wm_h = int(wm_w * icon.height / icon.width)
    if wm_h > icon.height:
        wm_h = icon.height
        wm_w = int(wm_h * icon.width / icon.height)

    icon_resized = icon.resize((wm_w, wm_h), Image.LANCZOS)

    r, g, b, a = icon_resized.split()
    a = a.point(lambda x: int(x * opacity))
    icon_resized = Image.merge('RGBA', (r, g, b, a))

    x = (iw - wm_w) // 2
    y = (ih - wm_h) // 2
    img.paste(icon_resized, (x, y), icon_resized)

    result = img.convert('RGB')
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/watermark', methods=['POST'])
def watermark():
    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        return 'No images uploaded', 400

    opacity = float(request.form.get('opacity', 25)) / 100
    size = float(request.form.get('size', 30)) / 100

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if f.filename == '':
                continue
            try:
                uploaded = Image.open(f.stream)
                result = apply_watermark(uploaded, opacity, size)
                img_buf = io.BytesIO()
                result.save(img_buf, 'JPEG', quality=92)
                img_buf.seek(0)
                zf.writestr('empanadas_' + f.filename, img_buf.read())
            except Exception as e:
                zf.writestr('_error_' + f.filename, str(e))
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/zip',
        as_attachment=True,
        download_name='empanadas_watermarked.zip'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
