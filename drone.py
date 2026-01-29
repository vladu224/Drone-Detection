from ultralytics import YOLO
import cv2
import numpy as np


MODEL_PATH = "best.pt"
VIDEO_LIST = ["Drone-1.mp4",
              "Drone-2.mp4",
              "Drone-3.mp4",
              "Drone-4.mp4"]

model = YOLO(MODEL_PATH)

# pt. accentuarea detaliilor
kernel_sharp = np.array([[0, -1, 0],
                         [-1, 5, -1],
                         [0, -1, 0]])


print(f"[START] Incepem procesarea...")

for video_name in VIDEO_LIST:

    cap = cv2.VideoCapture(video_name)

    # confidence pt drone
    confidence_list = []

    while True:
        # Citim urmatorul frame
        succes, frame = cap.read()
        
        # oprim bucla daca nu sunt frame-uri
        if not succes:
            break
        
        # aplicam filtrul
        filtered_frame = cv2.filter2D(frame, -1, kernel_sharp)

        # detectia
        results = model.predict(filtered_frame, imgsz=960,conf=0.8, verbose=False) 

        # extragem doar box-urile in care au fost incadrate drone
        drones = results[0].boxes
        
        # daca s-au gasit drone
        if results is not None:
            # luam scorurile de incredere
            scores = drones.conf.cpu().numpy()
            # le adaugam la lista noastra generala
            if len(scores) > 0:
                confidence_list.extend(scores)

        
        # Desenam chenarele peste imaginea procesata. 
        annotated_frame = results[0].plot(line_width=2, font_size=1)
        
        # Afisam fereastra cu rezultatul in timp real
        cv2.imshow("Detectie Drone", annotated_frame)

        # Asteptam 1 ms sa vedem daca utilizatorul apasa tasta 'q' pentru a iesi
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Intrerupere manuala de la tastatura.")
            break

    cap.release()

    # statistici
    print(f"\n--- RAPORT PENTRU: {video_name} ---")
    
    # macar 1 drona => calculam statisticile
    if len(confidence_list) > 0:
        # calculam media aritmetica a increderii
        media = np.mean(confidence_list)
        # luam maximul de inceredere
        maxim = np.max(confidence_list)
        
        # Afisam rezultatele in procente
        print(f" Numar cadre cu DRONE:  {len(confidence_list)}")
        print(f" MAX CONFIDENCE:        {maxim * 100:.2f}%")
        print(f" MEAN CONFIDENCE:       {media * 100:.2f}%")
    else:
        
        print("Nu s-au detectat DRONE in acest video.")
    
    print("------------------------------------------")


cv2.destroyAllWindows()
print("\n[INFO] Toate videoclipurile au fost procesate!")