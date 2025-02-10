# Bismillah
import requests as req
import cv2
from pyzbar import pyzbar
from pydub import AudioSegment
from pydub.playback import play
from app import call_api


def scan_product():
    # capture webcams
    capture = cv2.VideoCapture(0)
    # sound track
    beep = AudioSegment.from_wav("beep.wav")

    array = []
    barcode = ""
    opened = capture.isOpened()
    while opened:
        success, frame = capture.read()
        # flip the image to make it look like you're staring at a mirror
        frame = cv2.flip(frame, 1)
        # use pyzbar to detect the bar code
        detect_bar = pyzbar.decode(frame)
        # if no barcode is detected:
        if not detect_bar:
            pass
        else:
            # capture every code in the bae code
            for code in detect_bar:
                if code.data != "":
                    play(beep)

                    code = str(code.data).strip("b").replace("'", "")
                    print("Barcode detected:", code)
                    val = call_api(code)
                    print(val)
                    array = frame
                    barcode = code
                    opened = False
            if not opened:
                break
        cv2.imshow("scanner", frame)
        if cv2.waitKey(1) == ord("q"):
            break
    # close all windows
    capture.release()
    cv2.destroyAllWindows()
    return {"code": barcode, "array": array}
