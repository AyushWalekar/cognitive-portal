# import the necessary packages
import time

import cv2
import dlib
import imutils
import numpy as np
from app.ApplicationContext import ApplicationContext
from app.DBThread import DBThread
from imutils.video import VideoStream
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject

from threading import Thread


class PeopleCounter(Thread):
    app_context = ApplicationContext.getApplicationContext()
    app_props = app_context.get_props()

    # to be moved to application starter
    db_thread = DBThread(int(app_props["db_thread"]['time_interval']), app_props["db_thread"]['in_min'])
    db_thread.start()
    confidence_level = float(app_props["people_counter_props"]["confidence_level"])
    skip_frames = int(app_props["people_counter_props"]["skip_frames"])
    # initialize the list of class labels MobileNet SSD was trained to
    # detect
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]

    # load our serialized model
    print("[INFO] loading model...")

    prototxt = app_props["people_counter_props"]["prototxt"]
    caffemodel = app_props["people_counter_props"]["caffemodel"]

    def __init__(self, input_source=None, source_name=None, skip_frames=None):
        Thread.__init__(self)
        self.input_source = input_source
        if source_name is None:
            if input_source is None:
                self.source_name = "Camera"
            else:
                self.source_name = input_source
        self.skip_frames = skip_frames
        if self.skip_frames is None:
            self.skip_frames = PeopleCounter.skip_frames
        self.__is_running = False
        self.net = cv2.dnn.readNetFromCaffe(PeopleCounter.prototxt, PeopleCounter.caffemodel)

    # def run_counter(self):
    def run(self):
        # net = cv2.dnn.readNetFromCaffe(PeopleCounter.prototxt, PeopleCounter.caffemodel)
        # if a video path was not supplied, grab a reference to the webcam
        if self.input_source is None:
            print("[INFO] starting video stream...")
            vs = VideoStream(src=0).start()
            time.sleep(2.0)
        # otherwise, grab a reference to the video file
        else:
            print("[INFO] opening video file...")
            vs = cv2.VideoCapture(self.input_source)

        # initialize the video writer (we'll instantiate later if need be)

        # initialize the frame dimensions (we'll set them as soon as we read
        # the first frame from the video)
        w = None
        h = None

        # instantiate our centroid tracker, then initialize a list to store
        # each of our dlib correlation trackers, followed by a dictionary to
        # map each unique object ID to a TrackableObject
        ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        trackers = []
        trackable_objects = {}

        # initialize the total number of frames processed thus far, along
        # with the total number of objects that have moved either up or down
        total_frames = 0
        total_down = 0
        total_up = 0

        # loop over frames from the video stream
        self.__is_running = True
        while self.__is_running:
            # grab the next frame and handle if we are reading from either
            # VideoCapture or VideoStream
            frame = vs.read()
            if self.input_source is not None:
                frame = frame[1]
            else:
                frame = frame
            # frame = frame[1] if input_source is None else frame

            # if we are viewing a video and we did not grab a frame then we
            # have reached the end of the video
            if self.input_source is not None and frame is None:
                break

            # resize the frame to have a maximum width of 500 pixels (the
            # less data we have, the faster we can process it), then convert
            # the frame from BGR to RGB for dlib
            frame = imutils.resize(frame, width=500)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # if the frame dimensions are empty, set them
            if w is None or h is None:
                (h, w) = frame.shape[:2]

            # initialize the current status along with our list of bounding
            # box rectangles returned by either (1) our object detector or
            # (2) the correlation trackers
            status = "Waiting"
            rects = []

            # check to see if we should run a more computationally expensive
            # object detection method to aid our tracker
            if total_frames % self.skip_frames == 0:
                # set the status and initialize our new set of object trackers
                status = "Detecting"
                trackers = []

                # convert the frame to a blob and pass the blob through the
                # network and obtain the detections
                blob = cv2.dnn.blobFromImage(frame, 0.007843, (w, h), 127.5)
                self.net.setInput(blob)
                detections = self.net.forward()

                # loop over the detections
                for i in np.arange(0, detections.shape[2]):
                    # extract the confidence (i.e., probability) associated
                    # with the prediction
                    confidence = detections[0, 0, i, 2]

                    # filter out weak detections by requiring a minimum
                    # confidence
                    if confidence > PeopleCounter.confidence_level:
                        # extract the index of the class label from the
                        # detections list
                        idx = int(detections[0, 0, i, 1])

                        # if the class label is not a person, ignore it
                        if PeopleCounter.CLASSES[idx] != "person":
                            continue

                        # compute the (x, y)-coordinates of the bounding box
                        # for the object
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (start_x, start_y, end_x, end_y) = box.astype("int")

                        # construct a dlib rectangle object from the bounding
                        # box coordinates and then start the dlib correlation
                        # tracker
                        tracker = dlib.correlation_tracker()
                        rect = dlib.rectangle(start_x, start_y, end_x, end_y)
                        tracker.start_track(rgb, rect)

                        # add the tracker to our list of trackers so we can
                        # utilize it during skip frames
                        trackers.append(tracker)

            # otherwise, we should utilize our object *trackers* rather than
            # object *detectors* to obtain a higher frame processing throughput
            else:
                # loop over the trackers
                for tracker in trackers:
                    # set the status of our system to be 'tracking' rather
                    # than 'waiting' or 'detecting'
                    status = "Tracking"

                    # update the tracker and grab the updated position
                    tracker.update(rgb)
                    pos = tracker.get_position()

                    # unpack the position object
                    start_x = int(pos.left())
                    start_y = int(pos.top())
                    end_x = int(pos.right())
                    end_y = int(pos.bottom())

                    # add the bounding box coordinates to the rectangles list
                    rects.append((start_x, start_y, end_x, end_y))

            # draw a horizontal line in the center of the frame -- once an
            # object crosses this line we will determine whether they were
            # moving 'up' or 'down'
            cv2.line(frame, (0, h // 2), (w, h // 2), (0, 255, 255), 2)

            # use the centroid tracker to associate the (1) old object
            # centroids with (2) the newly computed object centroids
            objects = ct.update(rects)

            # loop over the tracked objects
            for (objectID, centroid) in objects.items():
                # check to see if a trackable object exists for the current
                # object ID
                to = trackable_objects.get(objectID, None)

                # if there is no existing trackable object, create one
                if to is None:
                    to = TrackableObject(objectID, centroid)

                # otherwise, there is a trackable object so we can utilize it
                # to determine direction
                else:
                    # the difference between the y-coordinate of the *current*
                    # centroid and the mean of *previous* centroids will tell
                    # us in which direction the object is moving (negative for
                    # 'up' and positive for 'down')
                    y = [c[1] for c in to.centroids]
                    direction = centroid[1] - np.mean(y)
                    to.centroids.append(centroid)

                    # check to see if the object has been counted or not
                    if not to.counted:
                        # if the direction is negative (indicating the object
                        # is moving up) AND the centroid is above the center
                        # line, count the object
                        if direction < 0 and centroid[1] < h // 2:
                            total_up += 1
                            to.counted = True

                        # if the direction is positive (indicating the object
                        # is moving down) AND the centroid is below the
                        # center line, count the object
                        elif direction > 0 and centroid[1] > h // 2:
                            total_down += 1
                            to.counted = True

                # store the trackable object in our dictionary
                trackable_objects[objectID] = to

                # draw both the ID of the object and the centroid of the
                # object on the output frame
                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            # construct a tuple of information we will be displaying on the
            # frame
            info = [
                ("Up", total_up),
                ("Down", total_down),
                ("Status", status),
            ]
            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, h - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

            # increment the total number of frames processed thus far and
            # then update the FPS counter
            total_frames += 1
            # app_props.total_count =  totalDown - totalUp
            PeopleCounter.app_context.total_count += total_down - total_up

        self.stop_counter()

        # if we are not using a video file, stop the camera video stream
        if self.input_source is None:
            vs.stop()

        # otherwise, release the video file pointer
        else:
            vs.release()

        # close any open windows
        cv2.destroyAllWindows()

    def stop_counter(self):
        print("[INFO] stopping counter for: ", self.source_name)
        PeopleCounter.app_context.pc_obj_map.pop(self.source_name)
        self.__is_running = False


# to run: python PeopleCounter.py
# pc = PeopleCounter(input_source="videos/example_01.mp4")
# pc.start()
