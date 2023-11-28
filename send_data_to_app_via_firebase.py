# in case of problem importing from google.cloud
# try :  pip install --upgrade google-cloud-storage

import pyrebase
from io import BytesIO
import io
import imageio
import cv2
import numpy as np
import threading
import time

import firebase_admin
from firebase_admin import credentials, storage, db

# Initialize Firebase with your credentials
cred = credentials.Certificate(r'C:\\projects\\yolov8and_all_features_from_v7\\firebase-adminsdk-serviceAccount.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'remotecare-ce82a.appspot.com',
                                     'databaseURL': 'https://remotecare-ce82a.firebaseio.com'})

# Reference to Firebase Storage bucket
bucket = storage.bucket()

# Reference to Firebase Realtime Database
ref = db.reference('/images')

class FirebaseDB:
    def __init__(self, config, mail, password):
        self.config = config
        self.pyrebase = pyrebase.initialize_app(config)
        self.db = self.pyrebase.database()
        self.storage = self.pyrebase.storage()
        self.auth = self.pyrebase.auth()
        self.idToken = None
        # self.refreshToken = None
        # self.localId = None
        # self.expiresIn = None
        self.mail = mail
        self.password = password

        # Token refreshing thread
        self.refresh_token_thread = threading.Thread(target=self._refresh_token_thread, daemon=True)
        self.refresh_token_thread.start()

        #For firebase_admin interface, because pyrebase is not able to load numpy images (not from disk)
        self.config = config
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        self.storage = self.firebase.storage()
        self.auth = self.firebase.auth()

    def user_login(self, mail, password):
        self.mail = mail
        self.password = password

        if self.firebase != None:
            user = auth.sign_in_with_email_and_password(mail, password)
            if user:
                self.idToken = user["idToken"]
                # self.refreshToken = user["refreshToken"]
                # self.localId = user["localId"]
                # self.expiresIn = user["expiresIn"]

            else:
                print("user login problem. Login failed with user: ", {mail}, " ", {password})
        else:
            print("firebase not initialized correctly, so login failed")

    def add_data(self, path, data):
        self.db.child(path).push(data)

    def get_data(self, path):
        return self.db.child(path).get().val()

    #
    # opencv_image - Is a result of cv2.imread() - nparray
    # filename - how the image will be named at firebase storage
    # path_in_RT_DB - firebase location
    #
    #
    def add_image_and_save_to_RT_DB(self, opencv_image, filename, path_in_RT_DB):
        # Convert OpenCV image to bytes
        _, image_data = cv2.imencode('.jpg', opencv_image)

        # Create an in-memory binary stream
        image_stream = io.BytesIO(image_data)

        # Reference to the Firebase Storage bucket
        bucket = self.storage.bucket()

        # Create a blob (file) in the bucket
        blob = bucket.blob(f'images/{filename}')

        # Upload the image data to the blob
        blob.upload_from_file(image_stream, content_type='image/jpeg')

        # Get the download URL of the uploaded image
        download_url = blob.public_url

        self.db.child(path_in_RT_DB).push(download_url)


    def _refresh_token_thread(self):
        while True:
            self.firebase = pyrebase.initialize_app(self.config)  # Replace with your actual Firebase configuration
            self.db = self.firebase.database()
            self.storage = self.firebase.storage()
            self.auth = self.firebase.auth()

            user = self.auth.sign_in_with_email_and_password(self.mail, self.password)
            if user:
                self.idToken = user["idToken"]

            print("Token refresh cycle started")

            time.sleep(55 * 60)    # Refresh the token every 40 minutes

    def save_url(self, url):
        self.db = self.pyrebase.database()
        self.db.child('Rooms').child('Moshe_Cohen').child('Cam_0').child('data')

        # Set data at the child node
        self.db.update({
            'last_image_0': url,
            'cyclic_list_of_images': '0',
            'cyclic_list_start_pointer': '0',
            'cyclic_list_end_pointer': '0'
        })
        self.db = self.pyrebase.database()


    def firebase_admin_upload_np_image_to_storage(self, opencv_image, filename):
        # Convert OpenCV image to bytes
        _, image_data = cv2.imencode('.jpg', opencv_image)

        # Create an in-memory binary stream
        image_stream = io.BytesIO(image_data)

        # Reference to the Firebase Storage bucket
        firebase_admin_bucket = storage.bucket()

        # Create a blob (file) in the bucket
        blob = firebase_admin_bucket.blob(f'images/{filename}')

        # Upload the image data to the blob
        blob.upload_from_file(image_stream, content_type='image/jpeg')

        # Get the download URL of the uploaded image
        download_url = blob.public_url

        self.save_url(download_url)

        return download_url





# Usage example
if __name__ == "__main__":
    # Replace with your actual Firebase configuration

    config = {
        "apiKey": "AIzaSyCpWjvONF2eLfIxsFOKSJaM8oU4HvLiW-M",
        "authDomain": "480830608258-hsnsgpgooeov6v0cqdhcn5ba9ccqdg3g.apps.googleusercontent.com",
        "databaseURL": "https://remotecare-ce82a-default-rtdb.firebaseio.com",
        "storageBucket": "remotecare-ce82a.appspot.com",
        "serviceAccount": r"C:\\projects\\yolov8and_all_features_from_v7\\firebase-adminsdk-serviceAccount.json"
    }

    # Initialize FirebaseDB instance
    firebase_db = FirebaseDB(config, "shlomocohen2@gmail.com", "ZCBMnvx1!")

    image_path = "C://projects//yolov7_custom//yolov7//data//saba_regular//frame_1502.jpg"
    image_name_in_firebase = image_path.split('//')[-1]

    NP_image = cv2.imread(image_path)

    return_url = firebase_db.firebase_admin_upload_np_image_to_storage(NP_image, "NP_frame_1502.jpg")

    # Get data from database
    #result = firebase_db.get_data("example/path")













