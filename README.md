# Receipt Labeler
Label a receipt image into the following labels: Receipt, Logo, Shop detail, Parches summery , and Additional details, using trained [TensorFlow object detection model](https://github.com/tensorflow/models) and Faster-RCNN-Inception-V2 model from the [Model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md).

The model has been trained over manualy labeled receipt images, that can be found [here](https://github.com/urield94/ReceiptLabeler/tree/master/receipt_dataset), and than was integrated to a freindly user interface's application using python flask.

# Before cloning...
- The application was developed and tested on Ubuntu 18.04.2 LTS, they may be some modifications in the code for other platforms.
- The application was developed using Python 3.6

# Use
You can try the application with the test_receipt_img.jpg image in the reposetory or you can scan your own receipt image!

The application can be found here - http://tiny.cc/receipt-labeler

For development use, clone the reposetory using -

    git clone https://github.com/urield94/ReceiptLabeler.git
    
Install the requirements using - 

    pip install requirements.txt
    
And run the flask server using - 

    python -m flask run
    
The app will be up and ruuning and live at http://127.0.0.1:5000/

