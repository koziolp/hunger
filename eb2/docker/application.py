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

@application.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            print('filename: ' + filename)
            model = tf.keras.models.load_model('./my_model.h5')
           
            
            uploads_dir = tf.keras.utils.get_file(UPLOAD_FOLDER, origin="https://md-datasets-cache-zipfiles-prod.s3.eu-west-1.amazonaws.com/v4w72bsts5-1.zip", untar=False)
            print("DIRS")
            print(uploads_dir)
            data_dir = pathlib.Path(uploads_dir)
            print(data_dir)

            uploads_list = list(data_dir.glob('*'))
            print("FILES")
            print(uploads_list)
            for h in uploads_list:
                print(h)

                img = keras.preprocessing.image.load_img(h, target_size=(256, 256)) 
                img_array = keras.preprocessing.image.img_to_array(img)
                img_array = tf.expand_dims(img_array, 0) # Create a batch

                predictions = model.predict(img_array)
                score = tf.nn.softmax(predictions[0])
                class_names = ['Healthy', 'Late_Blight']
                classification_val = "This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score))
                print(classification_val)
                return "<!doctype html><title>Image classification</title><h1>{}</h1>".format(classification_val)
    return '''
    <html>
    <head><link rel="stylesheet" href="style.css"></head>
    <title>Fight Plant Disease</title>
    <img src="bayer.png"></img>
    <h1>Upload a new plant photo</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host="0.0.0.0", port=5000)