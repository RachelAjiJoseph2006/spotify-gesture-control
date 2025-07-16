import cv2
import mediapipe as mp
import spotipy
import time 
from spotipy.oauth2 import SpotifyOAuth
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

CLIENT_ID = "8a82bae1471844758127b13f9a2dd804"
CLIENT_SECRET = "870c785f6c2b470ca63aa3ecbc4d2d86"
REDIRECT_URI = "http://localhost:8080"
SCOPE = "user-modify-playback-state user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))


model_path = r"D:\rig induction program\gesture_recognizer.task" 

devices = sp.devices()
print("Available Devices:", devices)

last_gesture_time = 0 
gesture_cooldown = 3 

def gesture_callback(result, image, timestamp_ms):
    global last_gesture_time

    if result.gestures:
        gesture_name = result.gestures[0][0].category_name
        current_time = time.time()

        if current_time - last_gesture_time < gesture_cooldown:
            return 

        print(f"FOUND GESTURE: {gesture_name}")
        last_gesture_time = current_time 
        current=sp.current_playback()

        if gesture_name == "Thumb_Up":
            """if current["is playing"]:
                print("ALREADY PLAYING????")
            else:"""
            print("PLAYING SONGGGG")
            sp.start_playback()
        elif gesture_name == "Thumb_Down":
            print("PAUSING SONGGGG")
            sp.pause_playback()
        elif gesture_name == "Victory":
            print("NEXT SONGGGGG")
            sp.next_track()
        elif gesture_name == "Open_Palm":
            print("PREVIOUS SONGGGGG")
            sp.previous_track()
        elif gesture_name == "ILoveYou":
            print("RICKROLLED")
            sp.start_playback(uris=['spotify:track:4PTG3Z6ehGkBFwjybzWkR8'])

options = vision.GestureRecognizerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=gesture_callback
)

recognizer = vision.GestureRecognizer.create_from_options(options)


cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)


    recognizer.recognize_async(mp_image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))

    cv2.imshow("Spotify Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
