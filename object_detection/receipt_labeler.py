import os
import cv2
import math
import numpy as np
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


class ReceiptLabeler:
    def __init__(self):
        self.curr_dir_path = os.path.dirname(__file__)
        self.model_name = 'inference_graph'
        self.num_of_classes = 5
        self.path_to_graph = os.path.join(self.curr_dir_path, self.model_name, 'frozen_inference_graph.pb')
        self.path_to_labels = os.path.join(self.curr_dir_path, 'training', 'labelmap.pbtxt')

        label_map = label_map_util.load_labelmap(self.path_to_labels)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.num_of_classes,
                                                                    use_display_name=True)
        detection_graph = tf.Graph()

        self.category_index = label_map_util.create_category_index(categories)

        # Load the TensorFlow model into memory.
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.path_to_graph, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.sess = tf.compat.v1.Session(graph=detection_graph)

        # Define input and output tensors (i.e. data) for the object detection classifier
        # Input tensor is the image
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        # Number of objects detected
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    def lable_image(self, img_name):
        """
            :param img_name: Img name with image extension (e.g. "image.jpg").
            :return: Dict of images details - path, width, and height.
        """

        # expand image dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value.
        img_path = os.path.join(self.curr_dir_path, "tmp", img_name)
        original_image = cv2.imread(img_path)
        image = cv2.imread(img_path)
        image_expanded = np.expand_dims(image, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_expanded})

        # Get boxes sizes and positions
        _, label_roi = vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.60)

        # Crop the image to labeled sub-images
        label_imgs_details = {}
        image_pil = Image.fromarray(cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR))
        im_width, im_height = image_pil.size
        for label_and_score in label_roi:
            label = label_and_score.split(":")[0]
            ymin, xmin, ymax, xmax = label_roi[label_and_score]

            (left, right, top, bottom) = (math.floor(xmin * im_width), math.floor(xmax * im_width),
                                          math.floor(ymin * im_height), math.floor(ymax * im_height))
            label_img = image_pil.crop((left, top, right, bottom))
            numpy_image = np.array(label_img)

            label_img_to_save = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

            label_imgs_details[label] = {"path": img_path.replace(img_name, f'{label}_{img_name}'),
                                         "width": label_img.size[0],
                                         "height": label_img.size[1]}

            cv2.imwrite(label_imgs_details[label]["path"], label_img_to_save)

        return label_imgs_details
