import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Listbox
import xml.etree.ElementTree as ET
import os
import re
import html


class XMLIncrementerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Incrementer")

        # Set minimum size and center the window
        self.set_minimum_size(275, 375)
        self.center_window()

        # Initialize variables
        self.filepaths = []
        self.trees = []
        self.increment_value = tk.IntVar(value=1)
        self.tags = []

        # GUI Elements
        # Frame to hold load button and view files button
        self.load_frame = tk.Frame(root)
        self.load_frame.pack(pady=5)

        # Button to load XML files
        self.load_button = tk.Button(
            self.load_frame, text="Load XML Files", command=self.load_files
        )
        self.load_button.pack(side=tk.LEFT)

        # Button to view loaded files
        self.view_files_button = tk.Button(
            self.load_frame, text="...", command=self.view_loaded_files
        )
        self.view_files_button.pack(side=tk.LEFT, padx=5)

        # Label and Entry for tag to increment
        self.tag_label = tk.Label(root, text="Tag to Increment:")
        self.tag_label.pack(pady=5)

        self.tag_entry = tk.Entry(root)
        self.tag_entry.insert(0, "Type tag here...")
        self.tag_entry.pack(pady=5)
        self.tag_entry.bind("<FocusIn>", self.on_entry_click)
        self.tag_entry.bind("<KeyRelease>", self.show_suggestions)

        # Listbox to show tag suggestions
        self.suggestions_listbox = Listbox(root)
        self.suggestions_listbox.pack(pady=5)
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.select_suggestion)

        # Label and Entry for increment value
        self.increment_label = tk.Label(root, text="Increment Value:")
        self.increment_label.pack(pady=5)

        self.increment_entry = tk.Entry(root, textvariable=self.increment_value)
        self.increment_entry.pack(pady=5)

        # Button to increment tag
        self.increment_button = tk.Button(
            root, text="Increment", command=self.increment_tag
        )
        self.increment_button.pack(pady=5)

    # Method to set minimum size of the window
    def set_minimum_size(self, width, height):
        self.root.update_idletasks()
        self.root.minsize(width, height)

    # Method to center the window
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # Method to clear the tag entry when it is clicked
    def on_entry_click(self, event):
        if self.tag_entry.get() == "Type tag here...":
            self.tag_entry.delete(0, "end")  # delete all the text in the entry
            self.tag_entry.insert(0, "")  # Insert blank for user input

    # Method to load XML files
    def load_files(self):
        # Open file dialog to select XML files
        self.filepaths = filedialog.askopenfilenames(filetypes=[("XML files", "*.xml")])
        if not self.filepaths:
            return
        self.trees = []
        self.tags = []
        for filepath in self.filepaths:
            try:
                # Open and read the file
                with open(filepath, "r", encoding="iso-8859-1") as file:
                    content = file.read()
                # Unescape HTML entities
                content = html.unescape(content)
                # Parse the XML content
                tree = ET.ElementTree(ET.fromstring(content))
                self.trees.append((filepath, tree))
                # Extract tags from the content
                if not self.tags:
                    self.tags = self.extract_tags(content)
            except ET.ParseError as e:
                # Show error message if XML parsing fails
                messagebox.showerror(
                    "Error", f"Failed to load XML file {filepath}: {e}"
                )
                continue
            except Exception as e:
                # Show error message for any other exceptions
                messagebox.showerror(
                    "Error", f"Unexpected error loading file {filepath}: {e}"
                )
                continue
        if self.trees:
            # Show success message if files are loaded successfully
            messagebox.showinfo(
                "Success", f"{len(self.trees)} XML files loaded successfully."
            )
        else:
            # Show error message if no valid XML files are loaded
            messagebox.showerror("Error", "No valid XML files loaded.")

    # Method to extract tags from XML content
    def extract_tags(self, content):
        # Use regex to find all tags in the content
        tags = set(re.findall(r"<(?!/)([^>\s]+)", content))
        return sorted(tags)

    # Method to view loaded files
    def view_loaded_files(self):
        if not self.filepaths:
            messagebox.showinfo("Info", "No files loaded.")
            return

        # Create a new top-level window to show loaded files
        top = Toplevel(self.root)
        top.title("Loaded Files")
        top.geometry("300x200")

        # Text widget to display file names
        files_text = tk.Text(top)
        files_text.pack(expand=True, fill=tk.BOTH)

        for filepath in self.filepaths:
            # Insert file name into the text widget
            files_text.insert(tk.END, os.path.basename(filepath) + "\n")

    # Method to show tag suggestions
    def show_suggestions(self, event):
        typed_text = self.tag_entry.get()
        self.suggestions_listbox.delete(0, tk.END)
        for tag in self.tags:
            if typed_text.lower() in tag.lower():
                self.suggestions_listbox.insert(tk.END, tag)

    # Method to select a suggestion
    def select_suggestion(self, event):
        selected_tag = self.suggestions_listbox.get(
            self.suggestions_listbox.curselection()
        )
        self.tag_entry.delete(0, tk.END)
        self.tag_entry.insert(0, selected_tag)

    # Method to increment tag
    def increment_tag(self):
        if not self.trees:
            messagebox.showerror("Error", "No XML files loaded.")
            return

        tag = self.tag_entry.get()
        if not tag:
            messagebox.showerror("Error", "No tag specified.")
            return

        try:
            increment_value = int(self.increment_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Increment value must be an integer.")
            return

        for filepath, tree in self.trees:
            root = tree.getroot()
            elements = root.findall(f".//{tag}")

            if not elements:
                messagebox.showerror(
                    "Error",
                    f"No elements found with tag '{tag}' in file {os.path.basename(filepath)}.",
                )
                continue

            for elem in elements:
                text = elem.text
                if text and text.isdigit():
                    elem.text = str(int(text) + increment_value)
                elif text and text[-1].isdigit():
                    num_part = "".join(filter(str.isdigit, text))
                    non_num_part = text.rstrip("0123456789")
                    new_num = str(int(num_part) + increment_value)
                    elem.text = non_num_part + new_num
                else:
                    elem.text = (text if text else "") + str(increment_value)

            try:
                # Write the updated XML back to the file
                """I use encoding iso-8859-1 because that's the enconding of my XMLs.
                Modify if your XML Files have a different encoding"""
                tree.write(filepath, encoding="iso-8859-1")
                messagebox.showinfo(
                    "Success",
                    f"File {os.path.basename(filepath)} updated successfully.",
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to save XML file {filepath}: {e}"
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = XMLIncrementerApp(root)
    root.mainloop()
