# Receipt Labeler
Label a receipt image into the following labels: Receipt, Logo, Shop detail, Parches summery , and Additional details, using trained TensorFlow object detection model.

The model was trained over manualy labeled receipt images, and than was integrated to a freindly user interface's application using python flask.

# Use
The application can be found here - http://tiny.cc/receipt-labeler

For development use, clone the reposetory using -

    git clone https://github.com/urield94/ReceiptLabeler.git
    
Install the requirements using - 

    pip install requirements.txt
    
And run the flask server using - 

    python flask run
    
The app will be up and ruuning and live at http://127.0.0.1:5000/

