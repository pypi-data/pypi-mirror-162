# class ShynaFaceRecognition:
#     down_url = ""
#     user = str(os.popen("echo $USER").read()).strip("\n")
#     out_dir = "~/tmp/"
#     ftp_username = os.environ.get('ftp_username')
#     ftp_pass = os.environ.get("ftp_pass")
#
#     def get_face_img(self):
#         self.down_url = 'wget -P ' + self.out_dir + ' -r --ftp-user="' + self.ftp_username + '" --ftp-password="' + self.ftp_pass + '" ftp://www.shyna623.com/facefiles/Shivam.jpg'
#         os.popen(self.down_url).readline()
#
#     def make_face_encodings(self, file_path):
#         file_image = face_recognition.load_image_file(file_path)
#         try:
#             file_face_encoding = face_recognition.face_encodings(file_image)[0]
#             return file_face_encoding
#         except IndexError:
#             print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
#             return False
#         except UnboundLocalError:
#             print("Something bad happened, but you were not there")
#             return False
#
#     def check_face(self, compare_with):
#         match = False
#         file_image = face_recognition.load_image_file(compare_with)
#         try:
#             result = face_recognition.face_encodings(file_image)[0]
#             st_dir = "/home/" + self.user + "/tmp/www.shyna623.com/facefiles/"
#             for filename in os.listdir(st_dir):
#                 file_path = os.path.join(st_dir, filename)
#                 if os.path.isfile(file_path):
#                     st_result = self.make_face_encodings(file_path=file_path)
#                     if st_result is False:
#                         match = False
#                     else:
#                         match = face_recognition.compare_faces(st_result, result)
#                 else:
#                     match = False
#         except Exception as e:
#             print(e)
#         finally:
#             return match
#
