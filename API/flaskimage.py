from flask import Flask,render_template,request,jsonify
import io
from PIL import Image
app = Flask(__name__)

@app.route("/predict", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        file = request.files.get('file')
        if file is None or file.filename == "":
            return jsonify({"error": "no file"})
        Mode = str(request.form.get('Mode'))
        print(Mode)
        try:
            image_bytes = file.read()
            pillow_img = Image.open(io.BytesIO(image_bytes))
            pillow_img.save("Done.jpg")
            return {'Code':'Under test'}
        except Exception as e:
            return jsonify({"error": str(e)})
    return "OK"

if __name__ == '__main__':
    app.run(host='localhost', port=5000,debug=True)