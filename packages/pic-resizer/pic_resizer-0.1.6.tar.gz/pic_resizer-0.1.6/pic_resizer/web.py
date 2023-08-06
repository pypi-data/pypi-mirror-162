import io
from logging import debug
from flask import Flask, render_template, request, send_file
from PIL import Image
from .lib import image_resizing
from .utils import filepath2basename_without_extension, parse_file_size

app = Flask(__name__, template_folder="templates")


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        debug(f"form={request.form}")
        target_size = parse_file_size(request.form.get("size"))
        if target_size < 2000:
            return "Target size is too small", 400
        f = request.files["file"]
        with io.BytesIO() as buf:
            f.save(buf)
            if buf.getbuffer().nbytes < target_size:
                return "Image file is too small", 400
            with Image.open(buf) as im:
                debug(f"len(buf)={buf.getbuffer().nbytes}")
                debug(f"target_size={target_size}")
                target_im = image_resizing(im, target_size)
                with io.BytesIO() as target_buf:
                    target_im.save(
                        target_buf, format=im.format, quality=75, subsampling=0
                    )
                    debug(f"len(target_buf)={target_buf.getbuffer().nbytes}")
                    target_buf.seek(0)
                    try:
                        new_buf = io.BytesIO(target_buf.read())
                        return send_file(
                            new_buf,
                            as_attachment=True,
                            download_name=f"{filepath2basename_without_extension(f.filename)}_resized.{im.format.lower()}",
                            mimetype=f"image/{im.format.lower()}",
                        )
                    finally:
                        f.close()


def serve():
    app.run()
