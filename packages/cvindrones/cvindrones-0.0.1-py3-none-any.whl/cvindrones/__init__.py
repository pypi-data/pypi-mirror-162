import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0,min_detection_confidence=0.5,min_tracking_confidence=0.5,max_num_hands=1)
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

def bodyProcessor(img,draw=True):
    poseList = []
    area=0

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    if results.pose_landmarks:
        poseList = []
        if draw:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        #print(results.pose_landmarks)
        # print("--"*10)
        for i in results.pose_landmarks.landmark:
            height, width, fc = img.shape
            x = i.x
            y = i.y
            visiblity = i.visibility
            poseList.append([int(x * width), int(y * height), visiblity * 100])
        print(poseList)
        all_x = []
        all_y = []
        for i in poseList:
            if (i[2] > 50):
                all_x.append(i[0])
                all_y.append(i[1])
        min_x = min(all_x)
        max_x = max(all_x)
        min_y = min(all_y)
        max_y = max(all_y)

        overlay = img.copy()
        x, y, w, h = min_x, max_y, (max_x - min_x), (min_y - max_y)

        alpha = 0.4
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        area = abs(w * h)

        if draw:
            cv2.rectangle(img, (min_x, max_y), (max_x, min_y), (255, 182, 60), 2, cv2.FILLED)
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 200, 0), -1)
            cv2.putText(img, str(area), (x + w // 2, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                        cv2.LINE_AA)

        return [img,poseList,area]
    return [img,[0],0]

def handProcessor(image, draw=True):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            if draw:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                      mp_drawing_styles.get_default_hand_landmarks_style(),
                                      mp_drawing_styles.get_default_hand_connections_style())
            handlms = []

            c = 0
            for i in hand_landmarks.landmark:
                height, width, fc = image.shape
                x = (i.x) * width
                y = (i.y) * height
                handlms.append([c, int(x), int(y)])
                c = c + 1
            totalFingers = 0

            if (len(handlms) != 0):
                fingerTips = [8, 12, 16, 20]
                for i in fingerTips:
                    if (handlms[i][2] > handlms[i - 2][2]):
                        totalFingers += 1
            droneAction = "stationery"
            if (totalFingers == 4):
                droneAction = "Move forward"
            elif (totalFingers == 2):
                droneAction = "Move backward"
            else:
                droneAction = "Stationery"
            if draw:
                cv2.putText(image, droneAction, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            return [image, handlms]
        return [image, [0]]
    return [image, [0]]

def faceProcessor(image, draw=True):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, fc = image.shape
    results = face_detection.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.detections:
      #print(results.detections)
      detection_results = []
      for detection in results.detections:
          bbox = detection.location_data.relative_bounding_box
          bbox_points = {
              "xmin": int(bbox.xmin * width),
              "ymin": int(bbox.ymin * height),
              "width": int(bbox.width * width),
              "height": int(bbox.height * height)
          }

          detection_results.append(bbox_points)
      x = detection_results[0]['xmin']
      y = detection_results[0]['ymin']
      w = detection_results[0]['width']
      h = detection_results[0]['height']
      cx, cy = x+w//2,y+h//2
      if draw:
          cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
          cv2.circle(image,(cx,cy),2,(0,255,0),3)
          overlay = image.copy()
          cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 200, 0), -1)
          alpha = 0.4
          image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
      area = w*h
      return [image,area,[x,y,w,h]]

    return [image,0,[0,0,0,0]]