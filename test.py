# importing libraries
import cv2
import face_recognition as fr

# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture('media/telegram_users/337315288/video.mp4')

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video  file")

# Read until video is completed
while cap.isOpened():

    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret:

        # Display the resulting frame
        cv2.imshow('Frame', frame)
        rgb_frame = frame[:, :, ::-1]
        face_loc = fr.face_locations(rgb_frame)
        fare_enc = fr.face_encodings(rgb_frame, face_loc)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break

# When everything done, release 
# the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
