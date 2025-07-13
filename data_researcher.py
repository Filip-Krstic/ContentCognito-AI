import subprocess
import pyautogui
import time
import keyboard
import os
import threading
import pygetwindow as gw
import easyocr
import re
import sqlite3
from difflib import SequenceMatcher
import cv2
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import json
import ffmpeg
import base64




#################################################### STAGE 1 ####################################################
def prof_scn(save_path="temp_out", file_name="temp_screenshot.png"):
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, file_name)

    try:
        # Take a screenshot on the device and pull it to the PC
        adb_screencap_command = f"adb shell screencap -p /sdcard/{file_name}"
        adb_pull_command = f"adb pull /sdcard/{file_name} {file_path}"
        
        # Execute the commands
        os.system(adb_screencap_command)
        os.system(adb_pull_command)
        
        if os.path.exists(file_path):
            #print(f"Screenshot saved as {file_path}")
            return file_path
        else:
            print(f"Failed to save screenshot to {file_path}")
            return None
    except Exception as e:
        print(f"Failed to take a screenshot: {e}")
        return None

def prof_in(screenshot_path, target_image_path="temp_out/prof.png", scale_factor_range=(0.5, 2.0), step=0.1, threshold=0.88):
    screenshot = cv2.imread(screenshot_path)
    target_image = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)

    if screenshot is None:
        print(f"Error: Could not load screenshot from {screenshot_path}")
        return False
    if target_image is None:
        print(f"Error: Could not load target image from {target_image_path}")
        return False

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    for scale in np.arange(scale_factor_range[0], scale_factor_range[1], step):
        target_resized = cv2.resize(target_image, (int(target_image.shape[1] * scale), int(target_image.shape[0] * scale)))
        
        result = cv2.matchTemplate(screenshot_gray, target_resized, cv2.TM_CCOEFF_NORMED)

        if np.any(result >= threshold):
            print(f"Match found at scale: {scale}")
            return True

    return False
#################################################################################################################

#################################################### STAGE 2 ####################################################
def rec_templ(output_file, duration=5):
    try:
        time.sleep(2)
        absolute_path = os.path.abspath(output_file)
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        command = f"scrcpy --record \"{absolute_path}\" --no-playback --no-audio --window-title rec"
        
        process = subprocess.Popen(command, shell=True)

        time.sleep(duration)

        try:
            scrcpy_window = gw.getWindowsWithTitle('rec')
            if scrcpy_window:
                scrcpy_window[0].close()
            else:
                print("Scrcpy window not found.")
        except Exception as e:
            print(f"Failed to close scrcpy window: {e}")

        if os.path.exists(absolute_path):
            pass
        else:
            print(f"Error: Recording file not found at {absolute_path}")
        
        return process, absolute_path

    except Exception as e:
        print(f"Failed to start recording: {e}")
        return None, None

def stop_rec_templ(process):
    try:
        if process:
            process.terminate()
            process.wait()
        else:
            print("No recording process to stop.")
    except Exception as e:
        print(f"Failed to stop recording: {e}")

def sc_pc(save_path="temp_out", file_name="screenshot"):
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, f"{file_name}.png")
    adb_command = f"adb exec-out screencap -p > {file_path}"
    
    try:
        subprocess.run(adb_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to take a screenshot: {e}")

def re_coord(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            coords = [tuple(map(int, line.strip().split(':'))) for line in lines if line.strip()]
            return coords
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    except ValueError:
        print(f"Error: The file '{file_path}' does not contain valid coordinates in 'x:y' format.")
        return None

def do_c(x, y):
    pyautogui.click(x, y)

def do_scl():
    adb_command = "adb shell input swipe 500 1500 500 1000 300"
    subprocess.run(adb_command, shell=True)

import pyautogui
from time import sleep

def hashtag_c(x, start_y, end_y, step=8):
    with open('configurables/gnum.txt', 'r') as f:
        num = int(f.read()) + 1

    for y in range(start_y, end_y + 1, step):
        pyautogui.moveTo(x, y)
        pyautogui.click(x, y)
        sleep(0.2)  # Allow time for the system to process the click
        for i in range(1, num):
            image_name = f'configurables/getout{i}.PNG'
            try:
                image_location = pyautogui.locateOnScreen(image_name, confidence=0.88)
                if image_location:
                    print(f"Getout image '{image_name}' found at {image_location}!")
                    getout_coords = re_coord('configurables/getout.txt')
                    print(f"Coordinates from file: {getout_coords}")
                    if getout_coords:
                        pyautogui.moveTo(getout_coords[0][0], getout_coords[0][1])
                        sleep(0.3)
                        pyautogui.click(getout_coords[0][0], getout_coords[0][1])
                        return
                    else:
                        print("Failed to read coordinates from getout.txt.")
                        break
            except Exception as e:
                pass


        

def strt_rec(save_path="temp_out", file_name="3", duration=5):
    try:
        os.makedirs(save_path, exist_ok=True)
        output_path = os.path.join(save_path, f"{file_name}.mp4")

        process, file_path = rec_templ(output_path, duration)
        if process:
            pass
        else:
            print("Failed to start recording.")
    except Exception as e:
        print(f"Error in recording thread: {e}")

def step_2(coords,getout_coords):
    scrcpy_process = subprocess.Popen([
        "scrcpy",
        "--max-size", "1024",
        "--video-bit-rate", "2M",
        "--max-fps", "30",
        "--video-codec", "h265",
        "--video-encoder", "c2.exynos.hevc.encoder",
        "--window-x", "0",
        "--window-y", "0"
    ])
    time.sleep(2)
    
    if coords and len(coords) >= 2:
        start_coord = coords[0]
        end_coord = coords[1]
        start_x, start_y = start_coord
        end_x, end_y = end_coord

        recording_thread = threading.Thread(target=strt_rec, args=("temp_out", "3", 5))
        recording_thread.start()

        sc_pc(file_name="1")

        hashtag_c(
            x=start_x,
            start_y=start_y,
            end_y=end_y,
            step=7
        )

        sc_pc(file_name="2")

        if getout_coords:
            pyautogui.moveTo(getout_coords[0][0], getout_coords[0][1])
            time.sleep(0.3)
            pyautogui.click(getout_coords[0][0], getout_coords[0][1])
            time.sleep(0.1)
            pyautogui.click(getout_coords[0][0], getout_coords[0][1])
            pyautogui.click(getout_coords[0][0], getout_coords[0][1])
            
        recording_thread.join()

        scrcpy_process.terminate()
#################################################################################################################

#################################################### STAGE 3 ####################################################
def crop_image(input_image_path, output_image_path, top_pixels, bottom_pixels):
    image = Image.open(input_image_path)

    width, height = image.size

    box = (0, top_pixels, width, height - bottom_pixels)

    cropped_image = image.crop(box)

    cropped_image.save(output_image_path)

def get_crop_values_from_file(file_path):
    with open(file_path, 'r') as file:
        crop_values = file.read().strip()  
    top_pixels, bottom_pixels = map(int, crop_values.split(":"))  
    return top_pixels, bottom_pixels

def crop_video(input_video_path, output_video_path, top_pixels, bottom_pixels):
    crop_filter = f"crop=in_w:in_h-{top_pixels}-{bottom_pixels}:0:{top_pixels}"

    try:
        ffmpeg.input(input_video_path) \
            .output(output_video_path, vf=crop_filter, vcodec='libx264', acodec='aac', strict='experimental') \
            .run(capture_stdout=True, capture_stderr=True) 
    except ffmpeg.Error as e:
        print(f"An error occurred: {str(e)}")
        if e.stderr:
            print(f"stderr output: {e.stderr.decode()}")
        else:
            print("No stderr output available. Check ffmpeg installation and arguments.")

def classify_image_with_blip(image, processor, model, device):
    image_input = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        generated_ids = model.generate(**image_input)
    
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    
    return caption


def merge_texts(text1, text2):
    words1 = text1.split()
    words2 = text2.split()

    merged_words = words1[:]

    for word in words2:
        if word not in merged_words:
            merged_words.append(word)

    merged_text = " ".join(merged_words)
    return merged_text


# Helper function to convert image to base64
def image_to_base64(image_path):
    """Convert image to base64-encoded string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

# Sentiment analysis function
def analyze_sentiment(text):
    sentiment_score = sentiment_analyzer.polarity_scores(text)
    if sentiment_score['compound'] >= 0.05:
        return 'Positive'
    elif sentiment_score['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# Extract emotion from hashtags based on sentiment analysis
def extract_emotion_from_hashtags(hashtags):
    emotions = []
    for hashtag in hashtags:
        sentiment = analyze_sentiment(hashtag)
        emotions.append(sentiment)
    if emotions:
        most_common_emotion = Counter(emotions).most_common(1)[0][0]
        return most_common_emotion
    else:
        return 'Neutral'

# Check if a word exists in the sensible words database (either nltk or urban dictionary)
def is_sensible_word(word, db_connection, threshold=0.81):
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nltk_words'")
    nltk_exists = cursor.fetchone() is not None
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urban_words'")
    urban_exists = cursor.fetchone() is not None
    if not nltk_exists and not urban_exists:
        raise sqlite3.OperationalError("Neither 'nltk_words' nor 'urban_words' tables exist in the database.")
    
    words_in_db = []
    if nltk_exists:
        cursor.execute("SELECT word FROM nltk_words")
        words_in_db.extend([row[0] for row in cursor.fetchall()])
    if urban_exists:
        cursor.execute("SELECT word FROM urban_words")
        words_in_db.extend([row[0] for row in cursor.fetchall()])
    
    for db_word in words_in_db:
        similarity = SequenceMatcher(None, db_word.lower(), word.lower()).ratio()
        if similarity >= threshold:
            return True
    return False

# Main function to process image data and insert into database
def img_data_txt(image_path_1, image_path_2, video_path, thresh, num_frames=5):
    # Read and extract text from image 1
    results_1 = reader.readtext(image_path_1, detail=0)
    extracted_text_1 = " ".join(results_1)

    # Read and extract text from image 2
    results_2 = reader.readtext(image_path_2, detail=0)
    extracted_text_2 = " ".join(results_2)

    # Merge extracted texts
    merged_text = merge_texts(extracted_text_1, extracted_text_2)

    # Extract hashtags
    hashtags = re.findall(r"#\w+", merged_text)
    hashtags_text = "\n".join(hashtags)

    # Extract liked by people information
    liked_by_people_match = re.search(r"Liked by\s+(.*?)\s+others", merged_text)
    liked_by_people = liked_by_people_match.group(1) + " others" if liked_by_people_match else ""

    # Remove unwanted text from merged text
    text_in_img = merged_text
    for item in hashtags:
        text_in_img = text_in_img.replace(item, "")
    text_in_img = re.sub(r"\b\d+K\b", "", text_in_img)
    text_in_img = re.sub(r"\b\d+\b", "", text_in_img).strip()
    text_in_img = re.sub(r"^\s*Reels\b", "", text_in_img).strip()
    text_in_img = re.sub(r"Liked by\s+.*?\s+others", "", text_in_img).strip()
    text_in_img = re.sub(r"\s+", " ", text_in_img).strip()

    # Filter words based on database check
    db_path = "data\\wrd.db"
    connection = sqlite3.connect(db_path)
    filtered_words = []
    try:
        for word in text_in_img.split():
            if is_sensible_word(word, connection, thresh):
                filtered_words.append(word)
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        filtered_words = text_in_img.split()
    finally:
        connection.close()
    text_in_img = " ".join(filtered_words)

    # Analyze the sentiment of the text
    emotional_tone_text = analyze_sentiment(text_in_img)

    # Analyze the sentiment of the hashtags
    emotional_tone_hashtag = extract_emotion_from_hashtags(hashtags)

    # Visual classification from video frames
    visual_categories = []
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
        caption = classify_image_with_blip(frame, processor, model, device)
        visual_categories.append(caption)

    cap.release()

    combined_visual_category = " ".join(visual_categories)

    # Convert image 2 to base64
    base64_image_2 = image_to_base64(image_path_1)

    # Insert data into the database
    db_file = "temp_out/p-info.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS reels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            liked_by_people TEXT,
            context TEXT,
            emotional_tone_text TEXT,
            emotional_tone_hashtag TEXT,
            visual_category TEXT,
            image_base64 TEXT
        )
    ''')

    # Insert data into the reels table
    cursor.execute(''' 
        INSERT INTO reels (liked_by_people, context, emotional_tone_text, emotional_tone_hashtag, visual_category, image_base64) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (liked_by_people, text_in_img, emotional_tone_text, emotional_tone_hashtag, combined_visual_category, base64_image_2))

    # Insert hashtags into the hashtags table
    for hashtag in hashtags:
        cursor.execute(''' 
            INSERT INTO hashtags (hashtag, total_seen) 
            VALUES (?, 1) 
            ON CONFLICT(hashtag) DO UPDATE SET total_seen = total_seen + 1
        ''', (hashtag,))
    
    conn.commit()
    conn.close()

def step_3():

    files_to_delete = ["temp_out/c1.png", "temp_out/c2.png", "temp_out/c3.mp4"]
    for file in files_to_delete:
        try:
            os.remove(file)
        except:
            pass

    top_to_crop, bottom_to_crop = get_crop_values_from_file('configurables/crop.txt')

    crop_image('temp_out/1.png', 'temp_out/c1.png', top_to_crop, bottom_to_crop)
    crop_image('temp_out/2.png', 'temp_out/c2.png', top_to_crop, bottom_to_crop)
    crop_video('temp_out/3.mp4', 'temp_out/c3.mp4', top_to_crop, bottom_to_crop)

    img_data_txt("temp_out/c1.png", "temp_out/c2.png", "temp_out/c3.mp4", 0.46)
#################################################################################################################


print("STARTED")
prof_img = "temp_out/prof.png"
folder = "temp_out"
temp_img = "temp_screenshot.png"
coordinates_file_path = 'configurables/hashtag.txt'
getout_coords = re_coord('configurables/getout.txt')
coords = re_coord(coordinates_file_path)

device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
reader = easyocr.Reader(["en"])
sentiment_analyzer = SentimentIntensityAnalyzer()


while True:
    screenshot_path = prof_scn(folder, temp_img)

    if screenshot_path and os.path.exists(screenshot_path):
        is_found = prof_in(screenshot_path, prof_img)

        if is_found:
            print("Profile image found; running STEP 2...")
            step_2(coords,getout_coords)
            print("STEP 2 complete; running STEP 3...")
            step_3()
            print("ITERATION COMPLETE!")
            do_scl()
        else:
            do_scl()
            time.sleep(0.5)
    else:
        print("Error: Screenshot file not found.")
        break




