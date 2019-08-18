import json
import sched
import threading
import time
import uuid
import os
import logging

from flask import Flask, redirect, send_file, render_template, request, url_for
from werkzeug.utils import secure_filename
from object_detection.receipt_labeler import ReceiptLabeler

application = Flask(__name__)
application.config["DEBUG"] = True
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
application_PATH = os.getcwd()
IMG_LABELS = ["Receipt", "Logo", "Shop details", "Purchase summary", "Additional details"]
IMG_IDS = ["receipt", "logo", "sd", "ps", "ad"]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_file(path):
    os.remove(path)


@application.route("/")
def redirecter():
    return redirect("/index")


@application.route("/index")
def index():
    return render_template("main.html")


@application.route("/label", methods=["GET", "POST"])
def label():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = f'{secure_filename(file.filename.split(".")[0])}_{uuid.uuid4()}'
            file.save(f'{application_PATH}/object_detection/tmp/{filename}.jpg')
            return redirect(f'/labeler/{filename}')
    return redirect(request.url)


@application.route("/labeler/<path:filename>")
def labeler(filename):
    return render_template("labeler.html", len=len(IMG_LABELS), IMG_LABELS=IMG_LABELS, IMG_IDS=IMG_IDS)


def delete(filename):
    try:
        print(f"Deleting {filename}")

        labels = ["Logo_", "Shop details_", "Purchase summary_", "Additional details_", "Receipt_", ""]
        for label in labels:
            img_path = f'{application_PATH}/object_detection/tmp/{label}{filename}.jpg'
            try:
                if os.path.isfile(img_path):
                    os.remove(img_path)
            except Exception as e:
                logging.error(f"Error while deleting {img_path} - {e}")
                continue
    except Exception as e:
        logging.error(e)
        return redirect("/index")

def delete_sched(filename):
    s = sched.scheduler(time.time, time.sleep)
    s.enter(30, 1, delete, (filename,))
    s.run()

@application.route("/delete_and_return/<path:filename>")
def delete_and_return(filename):
    t = threading.Thread(target=delete, args=(filename,))
    t.start()
    return redirect("/index")


@application.route("/label_img/<path:filename>")
def label_img(filename):
    try:
        if os.path.isfile(f'{application_PATH}/object_detection/tmp/{filename}.jpg'):
            receipt_labeler = ReceiptLabeler()
            print(f"Start labeling {filename}")
            res = receipt_labeler.lable_image(f'{filename}.jpg')
            print(f"Finished!")
            t = threading.Thread(target=delete_sched, args=(filename,))
            t.start()
            return json.dumps(res)
        else:
            return "Failed"
    except Exception as e:
        logging.error(e)
        return "Failed"

@application.route("/get_logo/<path:filename>")
def get_logo(filename):
    return send_file(f'{application_PATH}/object_detection/tmp/Logo_{filename}.jpg')


@application.route("/get_sd/<path:filename>")
def get_sd(filename):
    return send_file(f'{application_PATH}/object_detection/tmp/Shop details_{filename}.jpg')


@application.route("/get_ps/<path:filename>")
def get_ps(filename):
    return send_file(f'{application_PATH}/object_detection/tmp/Purchase summary_{filename}.jpg')


@application.route("/get_ad/<path:filename>")
def get_ad(filename):
    return send_file(f'{application_PATH}/object_detection/tmp/Additional details_{filename}.jpg')


@application.route("/get_receipt/<path:filename>")
def get_receipt(filename):
    return send_file(f'{application_PATH}/object_detection/tmp/Receipt_{filename}.jpg')
