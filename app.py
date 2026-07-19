from vision.detector import VisionDetector

def main():
    detector = VisionDetector()
    detector.start_camera()
    
if __name__ == "__main__":
    main()