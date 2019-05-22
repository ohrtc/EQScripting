#see https://stackoverflow.com/questions/2081836/reading-specific-lines-only
import sched, time, threading, pyrebase

s = sched.scheduler(time.time, time.sleep)
lastIndex = 0

def main ():
    firebase = firebase_setup()
    db = firebase.database()
    print("Firebase is setup")
    data = {"sessionStart": "2019-05-22 11:39:49" , "sessionEnd": "2019-05-22 12:39:49"}
    db.child("sessions").push(data)
    print("Data pushed.")


def firebase_setup():
    txt = open("api_key.txt")
    config = {
        "apiKey": txt.read(),
        "authDomain": "testprojectforeq.firebaseapp.com",
        "databaseURL": "https://testprojectforeq.firebaseio.com",
        "storageBucket": "testprojectforeq.appspot.com",
        "serviceAccount": "serviceCredentials.json"
    }
    return pyrebase.initialize_app(config)
#run the main method
main()
