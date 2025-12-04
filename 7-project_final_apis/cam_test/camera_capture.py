# camera_capture.py
import cv2
import time

def capture_video(duration_sec=10, filename="video_output.avi"):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erreur : impossible d’ouvrir la caméra.")
        return

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    out = cv2.VideoWriter(filename,
                          cv2.VideoWriter_fourcc(*'XVID'),
                          20.0,
                          (frame_width, frame_height))

    start_time = time.time()
    while int(time.time() - start_time) < duration_sec:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording...', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Erreur lors de la capture.")
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Vidéo enregistrée : {filename}")

if __name__ == "__main__":
    capture_video()
