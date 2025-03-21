from collections import Counter
import re
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Function to count letters and words
def count_letters_and_words(text):
    # Count letters
    letter_counts = Counter(char.lower() for char in text if char.isalpha())
    
    # Count words
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    
    return letter_counts, word_counts

# Function to update statistics in real-time
def update_stats(event=None):
    text = text_input.get("1.0", tk.END).strip()
    letter_output.delete("1.0", tk.END)
    word_output.delete("1.0", tk.END)
    
    if text:
        # Get counts
        letter_counts, word_counts = count_letters_and_words(text)
        
        # Total characters and words
        total_chars = len(text)
        total_words = len(re.findall(r'\b\w+\b', text))
        total_letters = sum(letter_counts.values())
        total_digits = sum(1 for char in text if char.isdigit())
        total_special = total_chars - total_letters - total_digits - text.count(" ")
        
        # Display general statistics
        letter_output.insert(tk.END, "=== General Statistics ===\n")
        letter_output.insert(tk.END, f"Total Characters: {total_chars}\n")
        letter_output.insert(tk.END, f"Total Letters: {total_letters}\n")
        letter_output.insert(tk.END, f"Total Digits: {total_digits}\n")
        letter_output.insert(tk.END, f"Total Special Characters: {total_special}\n")
        letter_output.insert(tk.END, f"Total Words: {total_words}\n\n")
        
        # Display letter counts
        letter_output.insert(tk.END, "=== Letter Counts ===\n")
        for letter, count in sorted(letter_counts.items()):
            letter_output.insert(tk.END, f"{letter}: {count}\n")
        
        # Display word counts
        word_output.insert(tk.END, "=== Word Counts ===\n")
        for word, count in sorted(word_counts.items()):
            word_output.insert(tk.END, f"{word}: {count}\n")
        
        # Display top 5 most frequent letters and words
        top_letters = letter_counts.most_common(5)
        top_words = word_counts.most_common(5)
        
        letter_output.insert(tk.END, "\n=== Top 5 Letters ===\n")
        for letter, count in top_letters:
            letter_output.insert(tk.END, f"{letter}: {count}\n")
        
        word_output.insert(tk.END, "\n=== Top 5 Words ===\n")
        for word, count in top_words:
            word_output.insert(tk.END, f"{word}: {count}\n")
        
        # Calculate and display average word length
        if total_words > 0:
            avg_word_length = sum(len(word) for word in re.findall(r'\b\w+\b', text)) / total_words
            word_output.insert(tk.END, f"\nAverage Word Length: {avg_word_length:.2f}\n")
        
        # Find longest and shortest word
        words = re.findall(r'\b\w+\b', text)
        if words:
            longest_word = max(words, key=len)
            shortest_word = min(words, key=len)
            word_output.insert(tk.END, f"Longest Word: {longest_word}\n")
            word_output.insert(tk.END, f"Shortest Word: {shortest_word}\n")
    else:
        letter_output.insert(tk.END, "Please enter some text to analyze.")

# Function to upload a file
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            text = file.read()
            text_input.delete("1.0", tk.END)
            text_input.insert(tk.END, text)

# Function to save results to a file
def save_results():
    results = letter_output.get("1.0", tk.END) + word_output.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(results)
        messagebox.showinfo("Success", "Results saved successfully!")

# Function to search for a word and highlight it
def search_word():
    text = text_input.get("1.0", tk.END).strip()
    search_term = search_entry.get().strip().lower()
    
    if text and search_term:
        # Remove previous highlights
        text_input.tag_remove("highlight", "1.0", tk.END)
        
        # Count occurrences
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = words.count(search_term)
        
        # Highlight all occurrences
        start = "1.0"
        while True:
            start = text_input.search(search_term, start, stopindex=tk.END, nocase=True)
            if not start:
                break
            end = f"{start}+{len(search_term)}c"
            text_input.tag_add("highlight", start, end)
            start = end
        
        text_input.tag_config("highlight", background="yellow", foreground="black")
        messagebox.showinfo("Search Result", f"The word '{search_term}' appears {word_count} time(s).")
    else:
        messagebox.showwarning("Invalid Input", "Please enter some text and a search term.")

# Function to detect language
def detect_language():
    text = text_input.get("1.0", tk.END).strip()
    if text:
        try:
            language = detect(text)
            messagebox.showinfo("Language Detection", f"The detected language is: {language}")
        except:
            messagebox.showwarning("Error", "Language detection failed. Please try again.")
    else:
        messagebox.showwarning("Invalid Input", "Please enter some text to detect the language.")

# Function to summarize text
def summarize_text():
    text = text_input.get("1.0", tk.END).strip()
    if text:
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Use TF-IDF to rank sentences
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
        
        # Get top 3 sentences
        top_sentence_indices = sentence_scores.argsort()[-3:][::-1]
        summary = "\n".join([sentences[i] for i in top_sentence_indices])
        
        messagebox.showinfo("Text Summary", f"Summary:\n\n{summary}")
    else:
        messagebox.showwarning("Invalid Input", "Please enter some text to summarize.")

# Create the main window
root = tk.Tk()
root.title("TextMetrics - Text Analyzer")

# Create a label for instructions
instruction_label = tk.Label(root, text="Enter your text below or upload a file:")
instruction_label.pack(pady=5)

# Create a scrolled text input box
text_input = scrolledtext.ScrolledText(root, width=80, height=15, wrap=tk.WORD)
text_input.pack(pady=5)

# Bind the text input to update stats in real-time
text_input.bind("<KeyRelease>", update_stats)

# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

# Add an "Upload File" button
upload_button = tk.Button(button_frame, text="Upload File", command=upload_file)
upload_button.pack(side=tk.LEFT, padx=5)

# Add an "Analyze Text" button
analyze_button = tk.Button(button_frame, text="Analyze Text", command=update_stats)
analyze_button.pack(side=tk.LEFT, padx=5)

# Add a "Save Results" button
save_button = tk.Button(button_frame, text="Save Results", command=save_results)
save_button.pack(side=tk.LEFT, padx=5)

# Add a "Search Word" button
search_button = tk.Button(button_frame, text="Search Word", command=search_word)
search_button.pack(side=tk.LEFT, padx=5)

# Add a "Detect Language" button
language_button = tk.Button(button_frame, text="Detect Language", command=detect_language)
language_button.pack(side=tk.LEFT, padx=5)

# Add a "Summarize Text" button
summarize_button = tk.Button(button_frame, text="Summarize Text", command=summarize_text)
summarize_button.pack(side=tk.LEFT, padx=5)

# Create a frame for the search feature
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

# Add a search entry box
search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

# Create a scrolled text box for letter counts
letter_output = scrolledtext.ScrolledText(root, width=80, height=15, wrap=tk.WORD)
letter_output.pack(pady=5)

# Create a scrolled text box for word counts
word_output = scrolledtext.ScrolledText(root, width=80, height=15, wrap=tk.WORD)
word_output.pack(pady=5)

# Run the application
root.mainloop()