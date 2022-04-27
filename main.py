import cv2
import face_recognition
import os
from datetime import datetime


def encodings(images):
    encodeList = []
    for img in images:
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def boxTxt(img, name='Unknown', color=(0, 0, 255)):
    cv2.rectangle(img, (x1*4, y1*4), (x2*4, y2*4), color, 2)
    cv2.rectangle(img, (x1*4, y2*4-35), (x2*4, y2*4), color, cv2.FILLED)
    cv2.putText(img, name, (x1*4+6, y2*4-6),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)


def attendance(name):
    with open('Attendance.csv', 'r+') as report:
        data = report.readlines()
        names = []
        for line in data:
            entry = line.split(',')
            names.append(entry[0])
        if name not in names:
            present = datetime.now()
            date = present.strftime('%H:%M:%S')
            report.writelines(f'\n{name},{date}')


path = 'known/'
images = []
people = []
known_faces = os.listdir(path)
print("Files found: ")
for person in known_faces:
    cImg = cv2.imread(path+person)
    images.append(cImg)
    people.append(os.path.splitext(person)[0])
print(known_faces)

try:
    knownEncodings = encodings(images)
    print('Encoding is completed....')
except IndexError:
    print("Error... \nPossible issues: Provided known pictures' Face is not clear or No Face is Found")
    exit()
except:
    print('Unknown Error Faced....')
    exit()

capture = cv2.VideoCapture(0)

while True:
    success, img = capture.read()
    if success:
        check = True
        name = 'Unknown'
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        face = face_recognition.face_locations(imgS)
        encoded_face = face_recognition.face_encodings(imgS)

        for enFc, fcLoc in zip(encoded_face, face):
            matches = face_recognition.compare_faces(knownEncodings, enFc)
            face_distance = face_recognition.face_distance(
                knownEncodings, enFc)
            for i in range(len(face_distance)):
                if min(face_distance) == face_distance[i]:
                    matchIndex = i
            y1, x2, y2, x1 = fcLoc
            if matches[matchIndex]:
                name = people[matchIndex].upper()
                boxTxt(img, name, (0, 255, 0))
            else:
                boxTxt(img)
                check = False
        if check:
            if name != 'Unknown':
                attendance(name)

        key = cv2.waitKey(1)

        if key == 27:
            break
        if len(face) != 0:
            cv2.imshow('Cam', img)
        else:
            cv2.destroyAllWindows()
    else:
        print('Please check your Cam...')
        break

capture.release()
cv2.destroyAllWindows()
