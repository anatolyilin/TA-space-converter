import os
from flask import Flask, request, redirect, url_for , send_from_directory, flash
from werkzeug.utils import secure_filename
import zipfile
import shutil

UPLOAD_FOLDER = '/app'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Maple TA converter</title>
    <h1>Upload Maple TA module below: </h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # 1. unzip
    zip_ref = zipfile.ZipFile(UPLOAD_FOLDER+"/"+filename, 'r')
    zip_ref.extractall(UPLOAD_FOLDER+"/temp")
    zip_ref.close()
    # 2. remove spaces
    remove_space_dir(UPLOAD_FOLDER+"/temp/web_folders")
    # # 3. rezip
    print "RENAMING COMPLETE"
    filename_n = filename[:-4]
    new_zip = UPLOAD_FOLDER+"/converted_"+filename_n
    shutil.make_archive(new_zip, 'zip', UPLOAD_FOLDER+'/temp/')
    print "ZIPPING COMPLETE"
    os.remove(UPLOAD_FOLDER+"/"+filename)
    shutil.rmtree(UPLOAD_FOLDER+ '/temp/')
    os.makedirs(UPLOAD_FOLDER+ '/temp/')
    return send_from_directory(app.config['UPLOAD_FOLDER'],"converted_"+filename)

def remove_space_dir(dir):
    for filename_zip in os.listdir(dir):
        # if (" " in filename_zip) and not(os.path.isdir(dir)):
        if os.path.isdir(dir+"/"+filename_zip):
            print filename_zip, "dir"
            remove_space_dir(dir+"/"+filename_zip)
        else:
            print filename_zip, "not dir"
            if " " in filename_zip:
                filenamenew = filename_zip
                for ch in filename_zip:
                    if ch == " ":
                        filenamenew = filenamenew.replace(ch, "%20")
                        print filenamenew
                os.rename(dir+ "/" + filename_zip,
                          dir + "/" + filenamenew)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')