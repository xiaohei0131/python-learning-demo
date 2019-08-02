import cv2

url = 'rtsp://10.1.203.220/stream/'
cap = cv2.VideoCapture(url)
while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture  
cap.release()
cv2.destroyAllWindows()
