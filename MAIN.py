import tkinter as tk
import subprocess
import threading
import os
import sqlite3

# Function to check if there are at least 2 images in the 'configurables' folder
def check_config_editor_ready():
    # Check for image files in 'temp_out' folder
    image_files = [f.lower() for f in os.listdir('temp_out') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Check if there are at least 2 images and if "prof." is in any of the files
    prof_file_check = any(f.startswith("prof.") for f in image_files)
    
    return len(image_files) >= 1 and prof_file_check

# Function to check row count in the database
def get_database_row_count():
    db_path = os.path.join('temp_out', 'p-info.db')
    if not os.path.exists(db_path):
        return 0  # Database doesn't exist, return 0 rows

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reels")
        row_count = cursor.fetchone()[0]  # Get row count
        conn.close()
        return row_count
    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
        return 0  # If error occurs, assume no data

# Function to check if the 'temp_out_x1.txt' file exists
def check_x1_file_exists():
    return os.path.exists('temp_out/temp_out_x1.txt')

# Function to run a script and reopen the main menu after it finishes
def run_script(script_name, window):
    process = subprocess.Popen(["python", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

# Create the main menu window
def main_menu():
    window = tk.Tk()
    window.title("Main Menu")
    window.geometry("800x350")
    window.resizable(False, False)  # Make the window resizable

    title_label = tk.Label(window, text="RUN PROCEDURE", font=("Arial", 20))
    title_label.grid(row=0, column=0, columnspan=7, pady=10)

    button_frame = tk.Frame(window)
    button_frame.grid(row=1, column=0, columnspan=7, pady=10, sticky="nsew")

    # Check conditions
    config_ready = check_config_editor_ready()
    database_rows = get_database_row_count()
    x1_file_exists = check_x1_file_exists()

    # Determine script statuses (default to Not Ready)
    config_status = "Not Ready"
    data_status = "Not Ready"
    factsheet_status = "Not Ready"
    view_status = "Not Ready"

    if config_ready:
        config_status = "Ready"

        if database_rows >= 20:
            data_status = "COMPLETED"
        else:
            data_status = "Ready"

        if database_rows >= 20 and data_status == "COMPLETED":
            factsheet_status = "Ready"

            if x1_file_exists:
                factsheet_status = "COMPLETED"
                view_status = "Ready"

    # If View Factsheet is ready, update previous statuses
    if view_status == "Ready":
        config_status = "OK"
        data_status = "COMPLETED"
        factsheet_status = "COMPLETED"

    # If Factsheet Logic is NOT ready, then View Factsheet should also be NOT READY
    if factsheet_status == "Not Ready":
        view_status = "Not Ready"

    # If Data Researcher is NOT ready, then Factsheet Logic & View Factsheet should also be NOT READY
    if data_status == "Not Ready":
        factsheet_status = "Not Ready"
        view_status = "Not Ready"

    # If Config Editor is NOT ready, then everything else should be NOT READY
    if config_status == "Not Ready":
        data_status = "Not Ready"
        factsheet_status = "Not Ready"
        view_status = "Not Ready"

    # Function to create a status box
    def create_status_box(frame, status):
        status_label = tk.Label(frame, text=status, font=("Arial", 9),
                                bg="green" if status in ["Ready", "COMPLETED", "OK"] else "red",
                                width=20, height=1)
        return status_label

    # Function to determine if a button should be enabled
    def is_button_enabled(status):
        return status in ["Ready", "COMPLETED", "OK"]

    # Create labels for each stage
    config_label = create_status_box(button_frame, config_status)
    config_label.grid(row=0, column=0, padx=10, sticky="nsew")

    arrow1_label = tk.Label(button_frame, text=" → ", font=("Arial", 14))
    arrow1_label.grid(row=0, column=1, sticky="nsew")

    data_researcher_label = create_status_box(button_frame, data_status)
    data_researcher_label.grid(row=0, column=2, padx=10, sticky="nsew")

    arrow2_label = tk.Label(button_frame, text=" → ", font=("Arial", 14))
    arrow2_label.grid(row=0, column=3, sticky="nsew")

    factsheet_logic_label = create_status_box(button_frame, factsheet_status)
    factsheet_logic_label.grid(row=0, column=4, padx=10, sticky="nsew")

    arrow3_label = tk.Label(button_frame, text=" → ", font=("Arial", 14))
    arrow3_label.grid(row=0, column=5, sticky="nsew")

    view_factsheet_label = create_status_box(button_frame, view_status)
    view_factsheet_label.grid(row=0, column=6, padx=10, sticky="nsew")

    # Create buttons
    config_button = tk.Button(button_frame, text="Config Editor", width=20, height=2,
                              state=tk.NORMAL if is_button_enabled(config_status) else tk.DISABLED,
                              command=lambda: threading.Thread(target=run_script, args=("config_editor.py", window)).start())
    config_button.grid(row=1, column=0, padx=10, sticky="nsew")

    data_researcher_button = tk.Button(button_frame, text="Data Researcher", width=20, height=2,
                                       state=tk.NORMAL if is_button_enabled(data_status) else tk.DISABLED,
                                       command=lambda: threading.Thread(target=run_script, args=("data_researcher.py", window)).start())
    data_researcher_button.grid(row=1, column=2, padx=10, sticky="nsew")

    factsheet_logic_button = tk.Button(button_frame, text="Factsheet Logic", width=20, height=2,
                                       state=tk.NORMAL if is_button_enabled(factsheet_status) else tk.DISABLED,
                                       command=lambda: threading.Thread(target=run_script, args=("factsheet_logic.py", window)).start())
    factsheet_logic_button.grid(row=1, column=4, padx=10, sticky="nsew")

    view_factsheet_button = tk.Button(button_frame, text="View Factsheet", width=20, height=2,
                                      state=tk.NORMAL if is_button_enabled(view_status) else tk.DISABLED,
                                      command=lambda: threading.Thread(target=run_script, args=("view_factsheet.py", window)).start())
    view_factsheet_button.grid(row=1, column=6, padx=10, sticky="nsew")

    # Instructions label
    instructions = (
        "1. Set up configurations based on your computer's specifications (e.g., set pixel dimensions as X:Y).\n"
        "2. Set up your profile picture in the configuration section.\n"
        "3. Connect your mobile phone with USB debugging enabled, then run Data Researcher.\n"
        "4. Once enough data is collected, run Factsheet Logic.\n"
        "5. Finally, run 'View Factsheet' to display the collected information."
    )

    instructions_label = tk.Label(window, text=instructions, font=("Arial", 10), justify="left", padx=20)
    instructions_label.grid(row=2, column=0, columnspan=7, pady=20, sticky="nsew")

    by = tk.Label(window, text="By 8982", font=("Arial", 8), justify="center", padx=20)
    by.grid(row=3, column=0, columnspan=1, pady=20, sticky="nsew")


    window.mainloop()

# Run the main menu
if __name__ == "__main__":
    main_menu()
