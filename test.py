from flask import Flask, send_from_directory, request,jsonify,abort,render_template
import plagarism
import os

#pt.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','bmp','pdf','svg'])
app = Flask(__name__)

UPLOAD_DIRECTORY = "C:/Users/Ademola/OneDrive/folder/OneDrive/Documents"
upload_html = 'C:/Users/Ademola/Desktop/upload.html'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


# route and function to handle the upload page
@app.route('/', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template(upload_html, msg='No file selected')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            return render_template(upload_html, msg='No file selected')

        if file and allowed_file(file.filename):

            # call the OCR function on it
            extracted_text = plagarism.sim(file)

            if extracted_text == '':
                replyy = 'Sorry Character could not be clearly recognized'
                return render_template(upload_html,
                                   msg=replyy)
            # extract the text and display it
            return render_template(upload_html,
                                   msg='Result',
                                   extracted_text=extracted_text)
    
    return render_template(upload_html)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run()

