# YouTube Singer Mashup Generator
[Live Demo](https://song-mashup-web-service.onrender.com/)

This project consists of two parts:
1.  **CLI Tool (`102353013.py`)**: A command-line utility to create audio mashups.
2.  **Web Service (`mashup_web/`)**: A Flask-based web interface for the mashup generator.

## Prerequisites

1.  **Python 3.7+**
2.  **FFmpeg**: The script uses a bundled FFmpeg binary, so a system-wide installation is **optional** but recommended.

## Installation

1.  Clone the repository or download the source code.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  (For Web App) Create a `.env` file in `mashup_web/` with your email credentials:
    ```
    EMAIL_USER=your_email@gmail.com
    EMAIL_PASS=your_app_password
    ```

## Usage

### CLI Tool
Run the script with the following arguments:
```bash
python 102353013.py <SingerName> <NumberOfVideos> <DurationEach> <OutputFileName>
```
Example:
```bash
python 102353013.py "The Weeknd" 10 20 mashup.mp3
```

### Web Service
1.  Navigate to `mashup_web` directory:
    ```bash
    cd mashup_web
    ```
2.  Run the Flask app:
    ```bash
    python app.py
    ```
3.  Open `http://localhost:5000` in your browser.
