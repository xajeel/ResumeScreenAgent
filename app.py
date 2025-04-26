# app.py
import os
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter import ttk

from src.dataextraction import get_pdf_files_in_directory, extract_text_from_pdf
from src.model import extract_candidate_info
from utils.savetocsv import save_candidates_to_csv

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "primary": "#4361ee",       # Primary accent color (royal blue)
    "primary_hover": "#3a56d4", # Darker shade for hover
    "secondary": "#f72585",     # Secondary accent (magenta)
    "success": "#4cc9f0",       # Success actions (cyan)
    "text_primary": "#2b2d42",  # Primary text (dark blue/black)
    "text_secondary": "#ffffff", # Secondary text (medium gray)
    "background": "#ffffff",    # Background (white)
    "card": "#f8f9fa",          # Card background (light gray)
    "border": "#e9ecef",        # Border color (lighter gray)
    "table_header": "#4361ee",  # Table header background
    "table_odd": "#f8f9fa",     # Table odd row
    "table_even": "#ffffff",    # Table even row
    "table_hover": "#e9f0ff"    # Table hover color
}

class ModernResumeParserApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Resume Parser")
        self.geometry("1100x800")
        self.configure(fg_color=COLORS["background"])
        
        # Set up grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Initialize variables
        self.job_description = ""
        self.pdf_files = []
        self.csv_file_path = ""
        self.data = None

        # Create UI elements
        self.create_header()
        self.create_content()
        self.create_footer()
    
    def create_header(self):
        # Main header frame with shadow effect
        header_container = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0, height=220)
        header_container.grid(row=0, column=0, sticky="ew")
        header_container.grid_propagate(False)
        
        # Title frame
        title_frame = ctk.CTkFrame(header_container, fg_color=COLORS["background"], corner_radius=0)
        title_frame.pack(fill="x", pady=(30, 20))
        
        # App title
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Resume Parser", 
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Select job description and resume files to analyze candidates", 
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Controls frame for file selection
        controls_frame = ctk.CTkFrame(
            header_container, 
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        controls_frame.pack(fill="x", padx=40, pady=10)
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        controls_frame.grid_rowconfigure(0, weight=1)
        controls_frame.grid_rowconfigure(1, weight=1)
        
        # Button style
        button_font = ctk.CTkFont(family="Helvetica", size=14)
        button_height = 46
        
        # Job description button
        job_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        job_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        job_desc_button = ctk.CTkButton(
            job_frame, 
            text="Select Job Description", 
            command=self.select_job_description,
            height=button_height,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            font=button_font,
            corner_radius=10
        )
        job_desc_button.pack(fill="x", pady=(0, 5))
        
        self.job_label = ctk.CTkLabel(
            job_frame,
            text="No job description selected",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.job_label.pack(fill="x")
        
        # Resumes folder button
        folder_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        folder_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        folder_button = ctk.CTkButton(
            folder_frame, 
            text="Select Resumes Folder", 
            command=self.select_folder,
            height=button_height,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            font=button_font,
            corner_radius=10
        )
        folder_button.pack(fill="x", pady=(0, 5))
        
        # Files button
        files_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        files_frame.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")
        
        files_button = ctk.CTkButton(
            files_frame, 
            text="Select Resume Files", 
            command=self.select_files,
            height=button_height,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            font=button_font,
            corner_radius=10
        )
        files_button.pack(fill="x", pady=(0, 5))
        
        self.files_label = ctk.CTkLabel(
            files_frame,
            text="No resume files selected",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.files_label.pack(fill="x")
        
        # Process Button
        self.process_button = ctk.CTkButton(
            controls_frame,
            text="Process Resumes",
            command=self.process_files,
            height=button_height,
            fg_color=COLORS["secondary"],
            hover_color="#d11a6f", 
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            corner_radius=10,
            state="disabled"
        )
        self.process_button.grid(row=1, column=0, columnspan=3, padx=20, pady=(5, 20), sticky="ew")
    
    def create_content(self):
        content_frame = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=0)  
        content_frame.grid_rowconfigure(1, weight=1) 
        
        progress_card = ctk.CTkFrame(
            content_frame, 
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        progress_card.grid(row=0, column=0, padx=0, pady=10, sticky="ew")
        progress_card.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ctk.CTkLabel(
            progress_card, 
            text="Ready to process files",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=COLORS["text_primary"]
        )
        self.progress_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_card,
            height=12,
            corner_radius=6,
            progress_color=COLORS["success"]
        )
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.progress_bar.set(0)

        self.results_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.results_card.grid(row=1, column=0, padx=0, pady=10, sticky="nsew")
        self.results_card.grid_columnconfigure(0, weight=1)
        self.results_card.grid_rowconfigure(0, weight=1)

        self.initial_label = ctk.CTkLabel(
            self.results_card, 
            text="Process resumes to see results",
            font=ctk.CTkFont(family="Helvetica", size=16),
            text_color=COLORS["text_secondary"]
        )
        self.initial_label.grid(row=0, column=0, padx=20, pady=20)
    
    def create_footer(self):
        footer_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"],
            height=60
        )
        footer_frame.grid(row=2, column=0, padx=40, pady=(10, 20), sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(1, weight=0)
        footer_frame.grid_propagate(False)

        self.csv_path_label = ctk.CTkLabel(
            footer_frame, 
            text="CSV file: Not generated yet",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.csv_path_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.open_folder_button = ctk.CTkButton(
            footer_frame, 
            text="Open Folder", 
            command=self.open_csv_folder,
            width=140,
            height=36,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            font=ctk.CTkFont(family="Helvetica", size=13),
            corner_radius=10,
            state="disabled"
        )
        self.open_folder_button.grid(row=0, column=1, padx=20, pady=10, sticky="e")
    
    def select_job_description(self):
        file_path = filedialog.askopenfilename(
            title="Select Job Description File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.job_description = file.read()
                self.job_label.configure(text=f"Selected: {os.path.basename(file_path)}")
                self.update_process_button_state()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load job description: {e}")
    
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Resume PDFs")
        
        if folder_path:
            self.pdf_files = get_pdf_files_in_directory(folder_path)
            self.files_label.configure(text=f"{len(self.pdf_files)} PDF files found in folder")
            self.update_process_button_state()
    
    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Resume PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_paths:
            self.pdf_files = list(file_paths)
            self.files_label.configure(text=f"{len(self.pdf_files)} PDF files selected")
            self.update_process_button_state()
    
    def update_process_button_state(self):
        if self.job_description and self.pdf_files:
            self.process_button.configure(state="normal")
        else:
            self.process_button.configure(state="disabled")
    
    def process_files(self):
        if not self.job_description:
            messagebox.showerror("Error", "Please select a job description first.")
            return
        
        if not self.pdf_files:
            messagebox.showerror("Error", "Please select resume files first.")
            return

        self.process_button.configure(state="disabled", text="Processing...")
        threading.Thread(target=self.run_processing, daemon=True).start()
    
    def run_processing(self):
        try:
            total_files = len(self.pdf_files)
            extracted_data = []
            
            for i, pdf_file in enumerate(self.pdf_files):
                file_name = os.path.basename(pdf_file)
                progress = (i / total_files)
                
                self.after(0, lambda p=progress, f=file_name: self.update_progress(p, f"Processing {f}"))
                
                text = extract_text_from_pdf(pdf_file)
                response = extract_candidate_info(self.job_description, text)
                extracted_data.append(response)
            
            self.after(0, lambda: self.update_progress(1.0, "Saving results to CSV..."))
            save_candidates_to_csv(extracted_data)
            
            import glob
            output_folder = "outputs"
            list_of_files = glob.glob(f"{output_folder}/candidates_*.csv")
            if list_of_files:
                self.csv_file_path = max(list_of_files, key=os.path.getctime)
                
                self.after(0, self.display_results)
            else:
                self.after(0, lambda: messagebox.showerror("Error", "CSV file not found after processing."))
                self.after(0, lambda: self.update_progress(0, "Processing failed"))
        
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred during processing: {e}"))
            self.after(0, lambda: self.update_progress(0, "Processing failed"))
        
        finally:
            self.after(0, lambda: self.process_button.configure(state="normal", text="Process Resumes"))
    
    def update_progress(self, value, status_text):
        self.progress_bar.set(value)
        self.progress_label.configure(text=status_text)
    
    def display_results(self):
        try:
            self.csv_path_label.configure(text=f"CSV file: {self.csv_file_path}")
            self.open_folder_button.configure(state="normal")
            
            df = pd.read_csv(self.csv_file_path)
            self.data = df
            
            for widget in self.results_card.winfo_children():
                widget.destroy()

            table_frame = ctk.CTkFrame(self.results_card, fg_color="transparent")
            table_frame.pack(expand=True, fill="both", padx=20, pady=20)
            style = ttk.Style()
            style.theme_use("clam")  
            
            style.configure("Treeview", 
                background=COLORS["background"],
                foreground=COLORS["text_primary"],
                rowheight=25,
                fieldbackground=COLORS["background"])
            
            style.configure("Treeview.Heading",
                background=COLORS["primary"], 
                foreground="white",
                relief="flat")
            
            style.map("Treeview.Heading",
                background=[('active', COLORS["primary_hover"])])
            
            style.map("Treeview",
                background=[('selected', COLORS["primary"])],
                foreground=[('selected', 'white')])
            
            # Create scrollbars
            vsb = ttk.Scrollbar(table_frame, orient="vertical")
            hsb = ttk.Scrollbar(table_frame, orient="horizontal")
            
            # Create the treeview table
            columns = list(df.columns)
            tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Configure scrollbars
            vsb.config(command=tree.yview)
            vsb.pack(side="right", fill="y")
            hsb.config(command=tree.xview)
            hsb.pack(side="bottom", fill="x")
            
            # Set column headings and widths
            for col in columns:
                tree.heading(col, text=col.upper())
                # Calculate appropriate column width based on content
                max_width = max(len(str(df[col].max())), len(col)) * 10 + 20
                tree.column(col, width=max_width, minwidth=100)
            
            # Insert data rows
            for i, row in df.iterrows():
                values = [row[col] for col in columns]
                tree.insert("", "end", values=values)
                
            # Add alternating row colors
            for i, item in enumerate(tree.get_children()):
                if i % 2 == 0:
                    tree.item(item, tags=('evenrow',))
                else:
                    tree.item(item, tags=('oddrow',))
                    
            tree.tag_configure('evenrow', background=COLORS["table_even"])
            tree.tag_configure('oddrow', background=COLORS["table_odd"])
            
            # Pack the treeview
            tree.pack(expand=True, fill="both")
            
            # Success message
            messagebox.showinfo("Success", f"Processing completed!\nResults saved to: {self.csv_file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display results: {e}")
    
    def open_csv_folder(self):
        if self.csv_file_path:
            folder_path = os.path.dirname(os.path.abspath(self.csv_file_path))
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS and Linux
                    import subprocess
                    subprocess.Popen(['open', folder_path] if os.uname().sysname == 'Darwin' else ['xdg-open', folder_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {e}")


if __name__ == "__main__":
    app = ModernResumeParserApp()
    app.mainloop()