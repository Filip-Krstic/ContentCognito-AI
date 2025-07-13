import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import threading
import tkinter as tk
import pyautogui

def run_in_thread():


    # Function to update the mouse position when 'C' is pressed
    def on_key_press(event):
        if event.char == 'c' or event.char == 'C':
            x, y = pyautogui.position()  # Get mouse position
            position_label.config(text=f"Mouse Position: X={x} Y={y}")


    # Creating the Tkinter GUI
    root = tk.Tk()
    root.title("Scrcpy and Mouse Position")

    # Add the label for instructions
    instruction_label = tk.Label(root, text="Press 'C' to grab mouse pos:")
    instruction_label.pack()

    # Add the label to display mouse position
    position_label = tk.Label(root, text="Mouse Position: X=0 Y=0")
    position_label.pack()

    # Bind the 'C' key to the on_key_press function
    root.bind("<KeyPress>", on_key_press)

    # Start the scrcpy process in a separate thread
    try:
        scrcpy_thread = threading.Thread(target=run_scrcpy)
        scrcpy_thread.daemon = True  # Allow thread to close when the main program closes
        scrcpy_thread.start()
    except:
        pass
    
    # Run the Tkinter event loop
    root.mainloop()

# Directory where configurables are stored
CONFIG_DIR = "configurables"
GNUM_FILE = os.path.join(CONFIG_DIR, "gnum.txt")

# Ensure the directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)


def get_gnum():
    """Read gnum.txt, return as integer, default to 0 if not found."""
    try:
        with open(GNUM_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def update_gnum():
    """Recalculate gnum based on existing getout[number].png files."""
    getout_files = [f for f in os.listdir(CONFIG_DIR) if f.startswith("getout") and f.lower().endswith(".png")]
    new_gnum = len(getout_files)
    with open(GNUM_FILE, "w") as f:
        f.write(str(new_gnum))



class ConfigManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurables Manager")
        self.root.geometry("600x500")

        self.tab_control = ttk.Notebook(root)

        # Tabs
        self.image_tab = ttk.Frame(self.tab_control)
        self.text_tab = ttk.Frame(self.tab_control)
        self.prof_image_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.image_tab, text="Manage Images")
        self.tab_control.add(self.text_tab, text="Manage Text Files")
        self.tab_control.add(self.prof_image_tab, text="Replace Prof Image")
        self.tab_control.pack(expand=1, fill="both")

        # Image Management UI
        self.setup_image_ui()

        # Text File Management UI
        self.setup_text_ui()

        # Prof Image Replacement UI
        self.setup_prof_image_ui()

    def setup_image_ui(self):
        frame = ttk.LabelFrame(self.image_tab, text="Images")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add label for image instructions
        image_instructions = ttk.Label(self.image_tab, text="Images should be gotten from Desktop screenshots", wraplength=550)
        image_instructions.pack(pady=5)

        self.image_listbox = tk.Listbox(frame, height=10)
        self.image_listbox.pack(side="left", fill="y", padx=5, pady=5)
        self.image_listbox.bind("<<ListboxSelect>>", self.display_image)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.image_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.image_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="left", padx=10)

        self.add_image_btn = ttk.Button(btn_frame, text="Add Image", command=self.add_image)
        self.add_image_btn.pack(fill="x", pady=5)

        self.remove_image_btn = ttk.Button(btn_frame, text="Remove Image", command=self.remove_image)
        self.remove_image_btn.pack(fill="x", pady=5)

        self.image_label = ttk.Label(self.image_tab)
        self.image_label.pack(pady=10)

        self.load_images()

    def setup_text_ui(self):

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        
        frame = ttk.LabelFrame(self.text_tab, text="Text Files")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add label for text file instructions
        text_instructions = ttk.Label(self.text_tab, text="Text files contain X pix: Y pix format. For hashtag.txt 1 entry is start, 2 is end.", wraplength=550)
        text_instructions.pack(pady=5)

        self.text_file_listbox = tk.Listbox(frame, height=10)
        self.text_file_listbox.pack(side="left", fill="y", padx=5, pady=5)
        self.text_file_listbox.bind("<<ListboxSelect>>", self.load_text_file)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.text_file_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.text_file_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="left", padx=10)

        self.save_text_btn = ttk.Button(btn_frame, text="Save Changes", command=self.save_text_file)
        self.save_text_btn.pack(fill="x", pady=5)

        self.text_editor = tk.Text(self.text_tab, height=15, wrap="none")
        self.text_editor.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_text_files()

    def setup_prof_image_ui(self):
        """Set up the Prof Image Replacement tab."""
        frame = ttk.LabelFrame(self.prof_image_tab, text="Replace Prof Image")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add label for profile image instructions
        prof_image_instructions = ttk.Label(self.prof_image_tab, text="Profile image should be gotten from a mobile phone's screenshot from an active reel.", wraplength=550)
        prof_image_instructions.pack(pady=5)

        self.replace_prof_btn = ttk.Button(frame, text="Replace Prof Image", command=self.replace_prof_image)
        self.replace_prof_btn.pack(fill="x", pady=5)

        self.prof_image_label = ttk.Label(self.prof_image_tab)
        self.prof_image_label.pack(pady=10)

        self.load_prof_image()

    def load_images(self):
        """Load images from the configurables directory."""
        self.image_listbox.delete(0, tk.END)
        for file in sorted(os.listdir(CONFIG_DIR)):
            if file.startswith("getout") and file.lower().endswith(".png"):
                self.image_listbox.insert(tk.END, file)
        update_gnum()  # Ensure gnum.txt is up to date

    def display_image(self, event):
        """Display the selected image."""
        selection = self.image_listbox.curselection()
        if not selection:
            return

        image_file = self.image_listbox.get(selection[0])
        image_path = os.path.join(CONFIG_DIR, image_file)

        try:
            image = Image.open(image_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)

            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def add_image(self):
        """Add a new image to the configurables directory."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])
        if not file_path:
            return

        # Get the next available getout[number].png
        gnum = get_gnum() + 1
        new_filename = f"getout{gnum}.PNG"
        new_path = os.path.join(CONFIG_DIR, new_filename)

        try:
            Image.open(file_path).save(new_path)
            update_gnum()
            self.load_images()
            messagebox.showinfo("Success", f"Image added as {new_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add image: {e}")

    def remove_image(self):
        """Remove the selected image."""
        selection = self.image_listbox.curselection()
        if not selection:
            return

        image_file = self.image_listbox.get(selection[0])
        image_path = os.path.join(CONFIG_DIR, image_file)

        if messagebox.askyesno("Confirm", f"Delete {image_file}?"):
            os.remove(image_path)
            update_gnum()
            self.load_images()
            self.image_label.config(image="")
            self.image_label.image = None

    def load_text_files(self):
        """Load text files from the configurables directory."""
        self.text_file_listbox.delete(0, tk.END)
        for file in sorted(os.listdir(CONFIG_DIR)):
            if file.endswith(".txt"):
                self.text_file_listbox.insert(tk.END, file)

    def load_text_file(self, event):
        """Load and display the selected text file."""  
        selection = self.text_file_listbox.curselection()
        if not selection:
            return

        text_file = self.text_file_listbox.get(selection[0])
        text_path = os.path.join(CONFIG_DIR, text_file)

        try:
            with open(text_path, "r") as f:
                content = f.read()

            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, content)
            self.current_text_file = text_path
        except Exception as e:
            messagebox.showerror("Error", f"Could not load text file: {e}")

    def save_text_file(self):
        """Save changes to the currently selected text file."""
        if not hasattr(self, "current_text_file"):
            messagebox.showerror("Error", "No file selected!")
            return

        content = self.text_editor.get("1.0", tk.END).strip()

        with open(self.current_text_file, "w") as f:
            f.write(content)

        messagebox.showinfo("Success", "Changes saved!")

    def load_prof_image(self):
        """Load and display the current prof.png if it exists."""  
        prof_image_path = os.path.join('temp_out', "prof.png")
        if os.path.exists(prof_image_path):
            try:
                image = Image.open(prof_image_path)
                image.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(image)

                self.prof_image_label.config(image=photo)
                self.prof_image_label.image = photo
            except Exception as e:
                messagebox.showerror("Error", f"Could not load prof.png: {e}")
        else:
            self.prof_image_label.config(text="No prof.png found")

    def replace_prof_image(self):
        """Allow the user to replace the prof.png image."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])
        if not file_path:
            return

        new_prof_image_path = os.path.join('temp_out', "prof.png")

        try:
            Image.open(file_path).save(new_prof_image_path)
            self.load_prof_image()  # Reload the new image
            messagebox.showinfo("Success", "prof.png has been replaced successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to replace prof.png: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigManagerApp(root)
    root.mainloop()
