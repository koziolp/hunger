import os
import pathlib
import tensorflow as tf
from tensorflow import keras
import numpy as np

from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

cwd = os.getcwd()
UPLOAD_FOLDER = cwd + "/tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

application = Flask(__name__,static_url_path='', static_folder='static')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def printPage(t, h):
    page =  '''
    <html>
    <head><link rel="stylesheet" href="style2.css"></head>
    <title>{}</title>
    <img src="bayer.png"></img>
    <h1>{}</h1>
    <h1>Upload a new plant photo</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''
    return page.format(t, h)


@application.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        remove_dir = application.config['UPLOAD_FOLDER']
        for f in os.listdir(remove_dir):
            os.remove(os.path.join(remove_dir, f))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print('file_path: ' + file_path)

            model = tf.keras.models.load_model('./my_model_v10.h5')
            
            print("file path to open:" + file_path)
            img = keras.preprocessing.image.load_img(file_path, target_size=(256, 256)) 
            img_array = keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0) # Create a batch

            predictions = model.predict(img_array)
            score = tf.nn.softmax(predictions[0])
            class_names = ['Healthy', 'Late_Blight']
            target_class = class_names[np.argmax(score)]
            classification_val = '';
            if target_class == 'Healthy':
                classification_val = "This image shows a {} plant with a {:.2f} percent confidence.".format(target_class, 100 * np.max(score))
            else:
                classification_val = "This image suggests the Late Blight disease with a {:.2f} percent confidence.".format(100 * np.max(score))
            print(classification_val)
            return printPage("Image classification", classification_val)
    return printPage("Fight Plant Disease", "")

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host="0.0.0.0", port=5000)