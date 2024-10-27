# Facial Emotion Recognition using OpenCV and Deepface
This part of the code implements real-time facial emotion detection using the `deepface` library and OpenCV. It captures video from the webcam, detects faces, and predicts the emotions associated with each face. The emotion labels are displayed on the frames in real-time.
Credit: Created by [Manish Tiwari](https://github.com/manish-9245/Facial-Emotion-Recognition-using-OpenCV-and-Deepface/tree/main), updated by [Sri Pranav Srivatsavai](https://github.com/sripranav9)

## Dependencies

- [deepface](https://github.com/serengil/deepface): A deep learning facial analysis library that provides pre-trained models for facial emotion detection. It relies on TensorFlow for the underlying deep learning operations.
- [OpenCV](https://opencv.org/): An open-source computer vision library used for image and video processing.

## Usage
### Initial steps:
- Git clone this repository Run: `git clone https://github.com/manish-9245/Facial-Emotion-Recognition-using-OpenCV-and-Deepface.git`
- Run: `cd Facial-Emotion-Recognition-using-OpenCV-and-Deepface`
1. Configure a new virtual environment
   - Create a new virtual environment: `conda create -n deepface-env python=3.8`
     - The version 3.8 fixes an issue where some libraries may not be compatible with newer versions of python.
   - Activate the environment: `conda activate deepface-env`
  
2. Install the required dependencies:
   - You can use `pip install -r requirements.txt`
   - Or you can install dependencies individually:
      - `pip install deepface`
      - `pip install tf_keras`
      - `pip install opencv-python`
    - Install Additional Dependencies as needed
      - Numpy: `conda install numpy`
      - Missing OpenCV data files (sometimes needed): `conda install -c conda-forge opencv`

3. The Haarcascade file should already be there, so there's no need to download the file again. But in case you have to:
   - Download the Haar cascade XML file for face detection:
     - Visit the [OpenCV GitHub repository](https://github.com/opencv/opencv/tree/master/data/haarcascades) and download the `haarcascade_frontalface_default.xml` file.

4. Run the code:
   - Execute the Python script.
   - The webcam will open, and real-time facial emotion detection will start.
   - Emotion labels will be displayed on the frames around detected faces.
