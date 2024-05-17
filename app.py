import cv2
import streamlit as st
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from time import sleep


def run_virtual_keyboard():
    # Use this line to capture video from the webcam
    cap = cv2.VideoCapture(0)

    # Set dimensions for the displayed video
    cap.set(3, 1280)
    cap.set(4, 720)
    detector = HandDetector(detectionCon=0.8)
    finalText = ''

    keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

    class Button():
        def __init__(self, pos, text, size=[100, 100]):
            self.pos = pos
            self.size = size
            self.text = text

    stop_button_pressed = False

    while cap.isOpened() and not stop_button_pressed:
        ret, img = cap.read()

        if not ret:
            st.write("The video capture has ended.")
            break

        imgOut = segmentor.removeBG(img, imgList[indexImg])

        hands, img = detector.findHands(imgOut)

        keyboard_canvas = np.zeros_like(img)
        buttonList = []

        for key in keys[0]:
            buttonList.append(Button([30 + keys[0].index(key) * 105, 30], key))

        for key in keys[1]:
            buttonList.append(Button([30 + keys[1].index(key) * 105, 150], key))

        for key in keys[2]:
            buttonList.append(Button([30 + keys[2].index(key) * 105, 260], key))

        buttonList.append(Button([90 + 10 * 100, 30], 'BS', size=[125, 100]))
        buttonList.append(Button([300, 370], 'SPACE', size=[500, 100]))

        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            if lmList:
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size

                    if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                        cv2.rectangle(img, button.pos, [button.pos[0] + button.size[0], button.pos[1] + button.size[1]],
                                      (0, 255, 160), -1)
                        cv2.putText(img, button.text, (button.pos[0] + 20, button.pos[1] + 70), cv2.FONT_HERSHEY_PLAIN,
                                    5, (255, 255, 255), 3)

                        l, _, _ = detector.findDistance(lmList[4][0:2], lmList[8][0:2], img, scale=0)

                        if l < 30:
                            cv2.rectangle(img, button.pos,
                                          [button.pos[0] + button.size[0], button.pos[1] + button.size[1]],
                                          (9, 9, 179), -1)
                            cv2.putText(img, button.text, (button.pos[0] + 20, button.pos[1] + 70),
                                        cv2.FONT_HERSHEY_PLAIN,
                                        5, (255, 255, 255), 3)
                            if button.text != 'BS' and button.text != 'SPACE':
                                finalText += button.text
                                textList = list(finalText)
                            elif button.text != 'SPACE':
                                if len(textList) != 0:
                                    textList.pop()
                                    text = ''
                                    finalText = text.join(textList)
                            else:
                                finalText += " "
                            sleep(0.25)

        cv2.putText(img, finalText, (120, 580), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        stacked_img = cv2.addWeighted(img, 0.7, keyboard_canvas, 0.3, 0)

        # Convert the frame from BGR to RGB format
        stacked_img = cv2.cvtColor(stacked_img, cv2.COLOR_BGR2RGB)

        # Display the frame using Streamlit's st.image
        st.image(stacked_img, channels="RGB")

        # Break the loop if the 'q' key is pressed or the user clicks the "Stop" button
        if stop_button_pressed:
            break

        key = cv2.waitKey(1)

        if key == ord('a'):
            if indexImg > 0:
                indexImg -= 1
        elif key == ord('d'):
            if indexImg < len(imgList) - 1:
                indexImg += 1
        elif key == ord('q'):
            break

    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()


# Set the title for the Streamlit app
st.title("AI Virtual Keyboard")

# Add a "Stop" button and store its state in a variable
stop_button_pressed = st.button("Stop")

# Run the virtual keyboard
run_virtual_keyboard()

