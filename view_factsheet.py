import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import base64
import io
import sqlite3

# Function to read data from the 'temp_out_x1.txt' file
def read_data_from_file(filename):
    mbti_data = {}
    hashtags_data = []
    sentiment_data = {"Optimist": 0, "Pessimist": 0}
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Extract MBTI data
                if line.startswith("MBTI<"):
                    mbti_data_str = line[len("MBTI<"):-2]  # Remove 'MBTI<' and '>' brackets
                    mbti_entries = mbti_data_str.split(",")
                    for entry in mbti_entries:
                        mbti_type, percentage = entry.split(":")
                        mbti_data[mbti_type] = float(percentage[:-1])  # Remove '%' and convert to float
                
                # Extract Hashtags data
                elif line.startswith("HTG<"):
                    hashtags_str = line[len("HTG<"):-2]  # Remove 'HTG<' and '>' brackets
                    hashtags_entries = hashtags_str.split(",")
                    for entry in hashtags_entries:
                        hashtag, total_seen = entry.split(":")
                        hashtags_data.append((hashtag, int(total_seen)))
                
                # Extract Sentiment data
                elif line.startswith("SENT<"):
                    sentiment_str = line[len("SENT<"):-2]  # Remove 'SENT<' and '>' brackets
                    sentiment_entries = sentiment_str.split(",")
                    for entry in sentiment_entries:
                        sentiment_type, percentage = entry.split(":")
                        sentiment_data[sentiment_type] = float(percentage[:-1])  # Remove '%' and convert to float
    except FileNotFoundError:
        messagebox.showerror("Error", f"File {filename} not found.")
    
    return mbti_data, hashtags_data, sentiment_data

# Function to fetch image data from the database (reels table)
def fetch_data_from_db():
    reels_data = []  # List to store base64 image data for the reels
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('temp_out/p-info.db')
        cursor = conn.cursor()

        # Query to fetch all base64 image strings from the "reels" table
        cursor.execute("SELECT image_base64 FROM reels")
        rows = cursor.fetchall()

        # Store each base64 string into the list
        for row in rows:
            reels_data.append(row[0])  # Each row has one column with the base64 string
        
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    
    return reels_data

# Function to decode base64 string and return a PIL image
def decode_base64_image(base64_str):
    img_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(img_data))
    return image

# Function to create the MBTI bar chart
def create_mbt_chart(mbti_data):
    fig, ax = plt.subplots(figsize=(6, 5))  # Adjusted size
    mbti_types = list(mbti_data.keys())
    percentages = list(mbti_data.values())
    
    ax.barh(mbti_types, percentages, color='skyblue')
    ax.set_xlabel('Percentage')
    ax.set_title('MBTI Distribution')
    return fig

# Function to create a pie chart for hashtags
def create_hashtag_pie_chart(hashtags_data):
    labels = [hashtag for hashtag, _ in hashtags_data]
    sizes = [total_seen for _, total_seen in hashtags_data]
    
    fig, ax = plt.subplots(figsize=(6, 5))  # Adjusted size
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie chart is circular
    ax.set_title('Top Hashtags Distribution')
    return fig

# Function to create a pie chart for sentiment
def create_sentiment_pie_chart(sentiment_data):
    labels = list(sentiment_data.keys())
    sizes = list(sentiment_data.values())
    
    fig, ax = plt.subplots(figsize=(6, 5))  # Adjusted size
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#4caf50', '#f44336'])
    ax.axis('equal')  # Equal aspect ratio ensures that pie chart is circular
    ax.set_title('Sentiment Distribution')
    return fig

# Function to update the image displayed on the Tkinter window
def update_image(image_label, reels_data, current_index, next_button, prev_button):
    if not reels_data:
        # Show a black placeholder with "No Image"
        black_placeholder = Image.new('RGB', (400, 400), color='black')
        photo = ImageTk.PhotoImage(black_placeholder)
        image_label.config(image=photo, text="No Image", font=("Arial", 16, "bold"), fg="white", bg="black")
        image_label.image = photo  # Keep a reference to the image to prevent garbage collection
        return

    if current_index < 0 or current_index >= len(reels_data):
        messagebox.showerror("Error", "Invalid image index.")
        return
    
    base64_str = reels_data[current_index]
    
    if base64_str is None:
        # Handle the case where the base64 string is None by showing the "No Image" placeholder
        black_placeholder = Image.new('RGB', (400, 400), color='black')
        photo = ImageTk.PhotoImage(black_placeholder)
        image_label.config(image=photo, text="No Image", font=("Arial", 16, "bold"), fg="white", bg="black")
        image_label.image = photo  # Keep a reference to the image to prevent garbage collection
        return
    
    # Proceed with decoding only if base64_str is not None
    try:
        image = decode_base64_image(base64_str)
        image = image.resize((400, 400))  # Resize image to fit the window
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo  # Keep a reference to the image to prevent garbage collection
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decode image: {e}")
        return

    # Hide "Previous" and "Next" buttons as needed
    if current_index == 0:
        prev_button.grid_remove()  # Hide "Previous" button on the first image
    else:
        prev_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")  # Show "Previous" button

    if current_index == len(reels_data) - 1:
        next_button.grid_remove()  # Hide "Next" button on the last image
    else:
        next_button.grid(row=2, column=2, padx=10, pady=10, sticky="e")  # Show "Next" button

# Function to embed a chart into the Tkinter window
def embed_chart_in_window(fig, window, row, col):
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

def main():
    # Initialize Tkinter window
    window = tk.Tk()
    window.title("Personality Data Visualizer")
    window.geometry("1200x1000")  # Adjust window size to accommodate all charts

    # Make the window resizable
    window.grid_rowconfigure(0, weight=1)  # For charts row
    window.grid_rowconfigure(1, weight=1)  # For the image row
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)

    # Read data from file (temp_out_x1.txt)
    mbti_data, hashtags_data, sentiment_data = read_data_from_file('temp_out/temp_out_x1.txt')

    # Check if data was loaded successfully
    if not mbti_data or not hashtags_data or not sentiment_data:
        messagebox.showerror("Error", "Data could not be loaded from the file.")
        window.quit()

    # Fetch data from the database for images
    reels_data = fetch_data_from_db()

    # Check if image data was loaded successfully
    if not reels_data:
        messagebox.showerror("Error", "No image data found in the database.")
        window.quit()

    # Create the MBTI, Hashtags, and Sentiment pie charts
    mbti_chart = create_mbt_chart(mbti_data)
    hashtags_chart = create_hashtag_pie_chart(hashtags_data)
    sentiment_chart = create_sentiment_pie_chart(sentiment_data)

    # Embed the charts in the window
    embed_chart_in_window(mbti_chart, window, row=0, col=0)
    embed_chart_in_window(hashtags_chart, window, row=0, col=1)
    embed_chart_in_window(sentiment_chart, window, row=0, col=2)

    # Create a frame for image display
    image_frame = tk.Frame(window)
    image_frame.grid(row=1, column=0, columnspan=2, pady=20)  # Take two columns for the image and listbox

    # Create a label to display the image
    image_label = tk.Label(image_frame)
    image_label.grid(row=0, column=0)

    # Create the list box for personality details next to the image
    listbox_frame = tk.Frame(window)
    listbox_frame.grid(row=1, column=2, pady=30, padx=40)

    listbox = tk.Listbox(listbox_frame, width=100, height=30)
    listbox.pack()

    # Get the highest MBTI
    highest_mbt_type = max(mbti_data, key=mbti_data.get)

    # Get the sentiment with the highest percentage
    highest_sentiment = max(sentiment_data, key=sentiment_data.get)

    # Add items to the listbox
    # Key traits for each MBTI type
    mbti_traits = {
        "INTJ": "      ~ Strategic, independent, problem-solver.",
        "INTP": "      ~ Curious, analytical, innovative.",
        "ENTJ": "      ~ Leadership, assertive, goal-oriented.",
        "ENTP": "      ~ Inventive, energetic, idea-driven.",
        "INFJ": "      ~ Idealistic, compassionate, insightful.",
        "INFP": "      ~ Creative, empathetic, values-driven.",
        "ENFJ": "      ~ Charismatic, empathetic, inspiring.",
        "ENFP": "      ~ Enthusiastic, sociable, visionary.",
        "ISTJ": "      ~ Practical, reliable, responsible.",
        "ISFJ": "      ~ Caring, loyal, supportive.",
        "ESTJ": "      ~ Organized, efficient, decisive.",
        "ESFJ": "      ~ Warm, sociable, community-focused.",
        "ISTP": "      ~ Independent, adaptable, hands-on.",
        "ISFP": "      ~ Creative, gentle, spontaneous.",
        "ESTP": "      ~ Energetic, bold, action-oriented.",
        "ESFP": "      ~ Playful, outgoing, entertaining."
    }

    # Assuming highest_mbt_type is already defined
    listbox.insert(tk.END, f"The person has a personality of '{highest_mbt_type}'.")
    listbox.insert(tk.END, mbti_traits.get(highest_mbt_type, "Traits not found."))
    listbox.insert(tk.END,"")
    listbox.insert(tk.END, f"The person is also a {highest_sentiment.upper()}.")
    if highest_sentiment == "Optimist":
        listbox.insert(tk.END,"      ~ Probably very social.")
        listbox.insert(tk.END,"      ~ Probably has a very healthy personal life.")
    elif highest_sentiment == "Pessimist":
        listbox.insert(tk.END,"      ~ Probably anti-social.")
        listbox.insert(tk.END,"      ~ Probably has deep personal issues.")
    
    listbox.insert(tk.END,"")
    listbox.insert(tk.END, "The person views a lot of topics related to:")
    for hashtag, _ in hashtags_data:
        listbox.insert(tk.END, f"      ~ {hashtag}")

    # Initialize image navigation
    current_index = 0

    # Create "Next" and "Previous" buttons
    next_button = tk.Button(window, text="Next", command=lambda: next_image())
    previous_button = tk.Button(window, text="Previous", command=lambda: previous_image())

    def next_image():
        nonlocal current_index
        if current_index < len(reels_data) - 1:
            current_index += 1
            update_image(image_label, reels_data, current_index, next_button, previous_button)

    def previous_image():
        nonlocal current_index
        if current_index > 0:
            current_index -= 1
            update_image(image_label, reels_data, current_index, next_button, previous_button)

    # Initialize with the first image and show buttons
    update_image(image_label, reels_data, current_index, next_button, previous_button)

    # Place navigation buttons under the image (below)
    next_button.grid(row=2, column=2, padx=10, pady=10, sticky="e")
    previous_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    # Start the Tkinter main loop
    window.mainloop()

# Run the main function
if __name__ == "__main__":
    main()
