# Video Labeler Tool

## Overview
The Video Labeler tool is a graphical user interface (GUI) application that allows users to label individual frames in a video. It provides an easy-to-use interface for adding, selecting, and managing labels for specific frames, with options to save and export the labeling data.

## Setup

### Prerequisites
- Python 3.10 or higher
- A virtual environment setup tool (e.g., `venv` or `virtualenv`)

### Installation

1. **Clone the Repository**  
   Clone the repository to your local machine.

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Install Dependencies**  
   Install the dependencies from the following Command
   ```bash
   pip install -r requirements.txt
   ```
### Usage
   Run the Application
   Start the Video Labeler tool by running the following command:
    ```bash
    python Video_Labeler.py
    ```
    or to import already existing action in text file, use 
        ```bash
    python video2.py
    ```
   1. **Select a Video**
       After launching the application, use the file explorer that appears to select the video file you wish to label.

   2. **Add Labels**
       Add labels by using the input section on the left side of the interface. This allows you to create new labels that can be assigned to specific frames in the video.

   3. **Select Added Labels**
       Once labels are created, you can select them from the dropdown menu to apply them to the current frame.

   4. **Navigate Through Frames**
      After assigning a label to a frame, click the "Save" button located near the frame navigation controls. This will save the label and automatically move to the next frame.

   5. **Export Individual Label Assignments**
      Use the "Save" button located at the top of the interface to export the label assignments for individual frames.

   6. **Save Label Mappings**
      To save the overall label mappings, use the button located at the top left of the interface. This saves all the label configurations and their assignments for the video.
