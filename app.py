import torch
from flask import Flask, render_template, request, send_from_directory
import os
from subprocess import Popen


UPLOAD_FOLDER = 'uploads'
DETECT_FOLDER = 'runs\detect'
BEST_WEIGHTS = 'best.pt'

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST" and 'file' in request.files:
        f = request.files['file']
        if f.filename != '':
            # Save the uploaded image
            filepath = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(filepath)

            # Run the detection process
            model = torch.hub.load('.', 'custom','best.pt', source='local')
            model.eval()
            process = Popen(["python", "detect.py", '--source', filepath, "--weights", BEST_WEIGHTS], shell=True)
            process.wait()

            # Get the latest result folder
            subfolders = [subfolder for subfolder in os.listdir(DETECT_FOLDER) if os.path.isdir(os.path.join(DETECT_FOLDER, subfolder))]
            latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(DETECT_FOLDER, x)))

            # Return the detected image
            image_path = os.path.join(DETECT_FOLDER, latest_subfolder, f.filename)
            print(image_path)
            return render_template('index.html', image_path=image_path)

    return render_template('index.html')


@app.route('/<path:filename>')
def display(filename):
    subfolders = [subfolder for subfolder in os.listdir(DETECT_FOLDER) if os.path.isdir(os.path.join(DETECT_FOLDER, subfolder))]
    latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(DETECT_FOLDER, x)))   
    directory = os.path.join(DETECT_FOLDER, latest_subfolder)
    file = os.path.basename(filename)
    return send_from_directory(directory, file)

if __name__ == "__main__":
    app.run(debug = True)

