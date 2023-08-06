
import cv2
import os
import numpy as np
import tensorflow as tf
from PIL import Image

def vd2img(inputfile, Snap_No = 1):
    for inpt in os.listdir(inputfile):
        try:
            a = inputfile+"/"+inpt
        except:
            a = inputfile+"\\"+inpt
        cap = cv2.VideoCapture(a)
        i = 0

        while(cap.isOpened()):
            ret, frame = cap.read()
            
            # This condition prevents from infinite looping
            # incase video ends.
            if ret == False:
                break
            
            # Save Frame by Frame into disk using imwrite method
            if i//Snap_No ==  0:
                name = inpt.split(".")[0]
                cv2.imwrite(name+str(i)+'.jpg', frame)
                i += 1
            else:
                i += 1


        cap.release()
        cv2.destroyAllWindows()

def cam2img(Snap_No = 1):
    cap = cv2.VideoCapture(0)
    i = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        
        if ret == False:
            break
        
        if i == Snap_No:
            break
        else:
            cv2.imwrite('Snap'+str(i)+'.jpg', frame)
            i += 1


    cap.release()
    cv2.destroyAllWindows()
    
def person_crop(img_path, threshhold):
    with tf.compat.v1.gfile.FastGFile('frozen_inference_graph.pb', 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.compat.v1.Session() as sess:
        sess.graph.as_default()
        tf.import_graph_def(graph_def, name='')

        path = img_path
        img = cv2.imread(path)
        rows = img.shape[0]
        cols = img.shape[1]
        inp = cv2.resize(img, (300, 300))
        inp = inp[:, :, [2, 1, 0]] 

        out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                        sess.graph.get_tensor_by_name('detection_scores:0'),
                        sess.graph.get_tensor_by_name('detection_boxes:0'),
                        sess.graph.get_tensor_by_name('detection_classes:0')],
                    feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})
        num_detections = int(out[0][0])
        for i in range(num_detections):
            classId = int(out[3][0][i])
            score = float(out[1][0][i])
            bbox = [float(v) for v in out[2][0][i]]
            if score > threshhold:
                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows
                param = (x,y,right,bottom)
                cv2.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)
                img2 = Image.open(path)
                im_crop = img2.crop(box=param)
                name_crop = "image"+str(i)+".jpg"
                im_crop.save(name_crop)
