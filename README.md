# Manga Read-Along Video Creator

## Overview

This repository contains a set of Python scripts designed to transform raw manga images and associated JSON data into engaging read-along videos. Inspired by children's voice books, the videos feature character speech bubbles that appear in sync with narration, providing an interactive experience for weebs. (yes I use ChatGPT to generate this)

## Features

- **Image Processing**: Use Magiv2 to get the transcript
- **Bubble Chat Animation**: Creates a dynamic speech bubble sequence corresponding to character dialogues.
- **Video Creation**: Converts the processed images into a video format using `img2mp4.py`, enabling smooth playback of the read-along experience.
- **Voice over**: Uses a TTS model to read out the dialogue extracted from the images. The TTS engine converts the text into natural-sounding speech, which is then synchronized with the bubble animations.

## Files Included

- `main.py`: The main file to run the whole process, is very buggy. But you can check the pipeline there
- `demo-manga-read-along.ipynb`: Check the process step-by-step here
- `requirements.txt`: Lists the dependencies needed to run the scripts.

## Usage

1. **Setup Environment**: 
   - Make sure you have Python installed.
   - Create a virtual environment (optional but recommended) and install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2.  **Prepare Your Data**:
    
    *   `\src\config.py`: Contains all the paths you need to know, this project requires users to provide manga images, character images, and voice bank samples for voice cloning
    *   Works best when the raw is in English and they are named in sequential order (e.g., `01.jpg`, `02.jpg`, `03.jpg`), the character naming format should be: `luffy_1.jpg`, `nami_1.jpg`.

3.  **Process Images and create Video with voice**:
    
    *   Check out the kaggle file.
    
4.  **View the Demo**:
    
    *   A video demo showcasing the read-along feature can be found in the repository.

Image Demo
----------

<div style="display: flex; justify-content: space-between;">
    <img src="https://github.com/user-attachments/assets/94ca1f19-74f9-4339-8325-b5caf5e63c55" alt="page_002_panel_000_bubble_000" style="width: 30%;"/>
    <img src="https://github.com/user-attachments/assets/8c2132b2-2972-46b3-ae35-c350fac6f079" alt="page_002_panel_000_bubble_001" style="width: 30%;"/>
    <img src="https://github.com/user-attachments/assets/b841dfbe-bf93-4258-9a14-09d9d7bd366c" alt="page_002_panel_000_bubble_002" style="width: 30%;"/>
</div>



Video Demo
----------

## No-Colour Full-Page Demo

https://github.com/user-attachments/assets/3463238e-dca4-4e1a-99d4-457c59960eec


## Colourized Panel-View Demo


https://github.com/user-attachments/assets/61ce8a2e-6fb7-40e2-859f-6ed804f50643


Contribution
------------

Feel free to fork the repository and submit pull requests if you have improvements or suggestions.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.
