import face_recognition
import cv2
from Shynatime import ShTime
from ShynaDatabase import Shdatabase
from ShynaProcess import ShynaLookForCameraUrl
import os


class ShynaFace:
    s_time = ShTime.ClassTime()
    s_data = Shdatabase.ShynaDatabase()
    s_process_cam = ShynaLookForCameraUrl.LookForCameraUrl()
    cam_url = []
    result = False
    num = 0
    down_url = ""
    user = str(os.popen("echo $USER").read()).strip("\n")
    out_dir = "/home/" + user
    ftp_username = os.environ.get('ftp_username')
    ftp_pass = os.environ.get("ftp_pass")
    process_this_frame = True

    def get_face_img(self):
        self.down_url = 'wget  -O ' + self.out_dir + '/Shivam.jpg -r --ftp-user="' + self.ftp_username + '" --ftp-password="' + self.ftp_pass + '" ftp://www.shyna623.com/facefiles/Shivam.jpg'
        os.popen(self.down_url).readline()

    def take_snap_shot_and_save(self, cam_url):
        try:
            # access the webcam (every webcam has a number, the default is 0)
            cap = cv2.VideoCapture(cam_url + "/video")
            while self.num < 1:
                ret, frame = cap.read()
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Only process every other frame of video to save time
                if self.process_this_frame:
                    face_location = face_recognition.face_locations(rgb_small_frame)
                    face_encoding = face_recognition.face_encodings(rgb_small_frame, face_location)
                    self.num = self.num + 1
            cv2.imwrite(os. path. join(self.out_dir, str(self.num) + '.jpg'), frame)
            print("Captured")
            cap.release()
            cv2.destroyAllWindows()
        except Exception:
            pass

    def check_if_me(self):
        self.s_data.set_date_system(process_name="shivam_face_check")
        self.cam_url = self.s_process_cam.get_cam_url()
        if str(self.cam_url).lower().__contains__('empty'):
            self.result = False
        else:
            if os.path.isfile(os.path.join(self.out_dir, "Shivam.jpg")):
                pass
            else:
                self.get_face_img()
            for i in range(len(self.cam_url)):
                self.take_snap_shot_and_save(cam_url=self.cam_url[i])
                unknown_image = face_recognition.load_image_file(os.path.join(self.out_dir, "1.jpg"))
                shiv_image = face_recognition.load_image_file(os.path.join(self.out_dir, "Shivam.jpg"))
                try:
                    unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
                    shiv_face_encoding = face_recognition.face_encodings(shiv_image)[0]
                except IndexError:
                    print("I wasn't able to locate any faces in at least one of the images. "
                          "Check the image files. Aborting...")
                    return "Not Same"
                except UnboundLocalError:
                    print("Something bad happened, but you were not there")
                    return "Not Same"
                known_faces = [
                    shiv_face_encoding, unknown_face_encoding
                ]
                self.result = face_recognition.compare_faces(known_faces, unknown_face_encoding)
                if bool(self.result[0]) is True:
                    print("Match")
                    self.s_data.default_database = os.environ.get("data_db")
                    self.s_data.query = "INSERT INTO shivam_face (task_date, task_time) VALUES('" \
                                        + str(self.s_time.now_date) + "', '" + str(self.s_time.now_time) + "')"
                    self.s_data.create_insert_update_or_delete()
                else:
                    pass


if __name__ == '__main__':
    ShynaFace().check_if_me()

