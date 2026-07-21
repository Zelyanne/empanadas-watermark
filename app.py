import os
import io
import zipfile
from flask import Flask, render_template, request, send_file
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

HERE = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(HERE, 'icone.jpeg')

icon_cache = None

def get_icon():
    global icon_cache
    if icon_cache is None:
        icon_cache = Image.open(ICON_PATH).convert('RGBA')
    return icon_cache.copy()

def apply_watermark(uploaded_image, opacity=0.25, size_percent=0.30):
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

    wm_img = Image.new('RGBA', (wm_w, wm_h), (0, 0, 0, 0))
    wm_img.paste(icon_resized, (0, 0), icon_resized)

    x = (iw - wm_w) // 2
    y = (ih - wm_h) // 2
    img.paste(wm_img, (x, y), wm_img)

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
