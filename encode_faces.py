import os
import cv2
import face_recognition
import pickle

def encode_faces(dataset_path="dataset", encoding_path="models/encodings.pkl"):
    known_encodings = []
    known_names = []

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset path '{dataset_path}' does not exist.")
        return

    # Loop over each person’s folder
    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)

        if not os.path.isdir(person_folder):
            continue

        print(f"[INFO] Processing images for {person_name}...")

        # Loop over each image in the person's folder
        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)

            # Load image and convert from BGR to RGB
            image = cv2.imread(image_path)
            if image is None:
                print(f"[WARNING] Unable to read {image_path}. Skipping.")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detect face locations and encode faces
            boxes = face_recognition.face_locations(rgb, model='hog')
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(person_name)

    # Ensure models directory exists
    os.makedirs(os.path.dirname(encoding_path), exist_ok=True)

    # Serialize encodings to file
    print("[INFO] Serializing encodings...")
    data = {"encodings": known_encodings, "names": known_names}
    with open(encoding_path, "wb") as f:
        pickle.dump(data, f)

    print(f"[INFO] Done! Encodings saved to {encoding_path}")
