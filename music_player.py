import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel
import pygame
from mutagen.mp3 import MP3

class Song:
    def __init__(self, music_file, artist, duration, album, genre):
        self.music_file = music_file
        self.artist = artist
        self.duration = duration
        self.album = album
        self.genre = genre

class Node:
    def __init__(self, song):
        self.song = song
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def add_song(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

    def delete_song(self, music_file):
        current = self.head
        while current:
            if current.song.music_file == music_file:
                if current.prev:
                    current.prev.next = current.next
                if current.next:
                    current.next.prev = current.prev
                if current == self.head:
                    self.head = current.next
                if current == self.tail:
                    self.tail = current.prev
                if current == self.current:
                    self.current = current.next if current.next else current.prev
                return current.song
            current = current.next
        return None

    def find_song(self, music_file):
        current = self.head
        while current:
            if current.song.music_file == music_file:
                return current.song
            current = current.next
        return None

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("900x500")
        self.root.configure(bg="#0B6477")

        self.song_list = DoublyLinkedList()
        self.deleted_songs = []
        self.update_history = []
        self.paused = False
        self.current_song_path = None

        self.init_player()
        self.init_ui()

    def init_ui(self):
        self.song_label = tk.Label(self.root, text="Now Playing: ", font=("Arial", 12), bg="#C8A8E9")
        self.song_label.pack(pady=(10, 0))

        self.song_listbox = tk.Listbox(self.root, width=80, height=15, font=("Arial", 10), bg="white")
        self.song_listbox.pack(pady=20)
        self.song_listbox.bind('<<ListboxSelect>>', self.on_select_song)  # Bind the selection event

        self.progress_bar_frame = tk.Frame(self.root, bg="#213A57")
        self.progress_bar_frame.pack(pady=20)

        self.elapsed_time_label = tk.Label(self.progress_bar_frame, text="0:00", font=("Arial", 10), bg="#073B4C")
        self.elapsed_time_label.grid(row=0, column=0)
        
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TProgressbar", background='blue') 

        self.progress_scale = ttk.Scale(self.progress_bar_frame, from_=0, to=1000, orient=tk.HORIZONTAL, length=800)
        self.progress_scale.grid(row=0, column=1)

        self.remaining_time_label = tk.Label(self.progress_bar_frame, text="0:00", font=("Arial", 10), bg="#073B4C")
        self.remaining_time_label.grid(row=0, column=2)

        button_bg = "#213A57" 
        button_fg = "white"

        self.button_frame = tk.Frame(self.root, bg="#073B4C")
        self.button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.add_button = tk.Button(self.button_frame, text="Add Song", command=self.add_song, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.add_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Song", command=self.delete_song, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.delete_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.show_button = tk.Button(self.button_frame, text="Show Playlist", command=self.show_playlist, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.show_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.update_button = tk.Button(self.button_frame, text="Update Song", command=self.update_song, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.update_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.deleted_button = tk.Button(self.button_frame, text="Show Deleted", command=self.show_deleted_songs, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.deleted_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.history_button = tk.Button(self.button_frame, text="Update History", command=self.show_update_history, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.history_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.volume_label = tk.Label(self.root, text="Volume: ", font=("Arial", 10), bg="#073B4C")
        self.volume_label.pack(side=tk.LEFT, padx=10, pady=(10, 0))

        self.volume_slider = ttk.Scale(self.root, from_=0, to=1, orient=tk.HORIZONTAL, length=200, command=self.set_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side=tk.LEFT, padx=10, pady=(10, 0))

        self.play_button = tk.Button(self.root, text="▶ Play", command=self.play_music, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.play_button.pack(side=tk.LEFT, padx=(50, 5), pady=5)

        self.pause_button = tk.Button(self.root, text="|| Pause", command=self.pause_music, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.prev_button = tk.Button(self.root, text="⏮ Previous", command=self.play_previous, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_button = tk.Button(self.root, text="Next ⏭", command=self.play_next, font=("Arial", 12), bg=button_bg, fg=button_fg)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

    def init_player(self):
        pygame.init()
        pygame.mixer.init()
        self.root.after(1000, self.update_progress)

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def add_song(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
        if file_path:
            music_file = file_path
            artist = "Unknown Artist"
            duration = str(int(MP3(file_path).info.length // 60)) + ":" + str(int(MP3(file_path).info.length % 60)).zfill(2)
            album = "Unknown Album"
            genre = "Unknown Genre"
            song = Song(music_file, artist, duration, album, genre)
            self.song_list.add_song(song)
            self.song_listbox.insert(tk.END, os.path.basename(music_file))

    def delete_song(self):
        selected_song_index = self.song_listbox.curselection()
        if selected_song_index:
            selected_song_index = int(selected_song_index[0])
            song_name = self.song_listbox.get(selected_song_index)

            song_node = self.song_list.head
            while song_node:
                if os.path.basename(song_node.song.music_file) == song_name:
                    deleted_song = self.song_list.delete_song(song_node.song.music_file)
                    if deleted_song:
                        self.deleted_songs.append(deleted_song)
                        self.song_listbox.delete(selected_song_index)
                        if self.current_song_path == deleted_song.music_file:
                            self.stop_music()
                        messagebox.showinfo("Song Deleted", f"Deleted: {song_name}")
                        self.update_playlist()
                    else:
                        messagebox.showwarning("Warning", "Failed to delete the song!")
                    return
                song_node = song_node.next
            messagebox.showwarning("Warning", "Song not found in the list!")
        else:
            messagebox.showwarning("Warning", "No song selected for deletion!")

    def update_playlist(self):
        self.song_listbox.delete(0, tk.END)
        current = self.song_list.head
        while current:
            self.song_listbox.insert(tk.END, os.path.basename(current.song.music_file))
            current = current.next

    def update_song(self):
        selected_song_index = self.song_listbox.curselection()
        if selected_song_index:
            selected_song_index = int(selected_song_index[0])
            song_name = self.song_listbox.get(selected_song_index)
            new_song_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
            if new_song_path:
                song_node = self.song_list.head
                while song_node:
                    if os.path.basename(song_node.song.music_file) == song_name:
                        old_song_file = song_node.song.music_file
                        self.update_history.append(f"Updated {song_name} to {os.path.basename(new_song_path)}")
                        song_node.song.music_file = new_song_path
                        song_node.song.duration = str(int(MP3(new_song_path).info.length // 60)) + ":" + str(int(MP3(new_song_path).info.length % 60)).zfill(2)
                        self.song_listbox.delete(selected_song_index)
                        self.song_listbox.insert(selected_song_index, os.path.basename(new_song_path))
                        if self.current_song_path == old_song_file:
                            self.play_music()
                        break
                    song_node = song_node.next
        else:
            messagebox.showwarning("Warning", "No song selected for updating!")

    def show_update_history(self):
        history_window = Toplevel(self.root)
        history_window.title("Update History")
        history_window.geometry("400x300")

        history_listbox = tk.Listbox(history_window, width=50, height=15)
        history_listbox.pack(padx=10, pady=10)

        for record in self.update_history:
            history_listbox.insert(tk.END, record)

    def show_deleted_songs(self):
        deleted_window = Toplevel(self.root)
        deleted_window.title("Deleted Songs")
        deleted_window.geometry("400x300")

        deleted_listbox = tk.Listbox(deleted_window, width=50, height=15)
        deleted_listbox.pack(padx=10, pady=10)

        for song in self.deleted_songs:
            deleted_listbox.insert(tk.END, os.path.basename(song.music_file))

    def show_playlist(self):
        playlist_window = Toplevel(self.root)
        playlist_window.title("Current Playlist")
        playlist_window.geometry("400x300")

        playlist_listbox = tk.Listbox(playlist_window, width=50, height=15)
        playlist_listbox.pack(padx=10, pady=10)

        current = self.song_list.head
        while current:
            playlist_listbox.insert(tk.END, os.path.basename(current.song.music_file))
            current = current.next

    def on_select_song(self, event):
        selected_song_index = self.song_listbox.curselection()
        if selected_song_index:
            selected_song_index = int(selected_song_index[0])
            song_name = self.song_listbox.get(selected_song_index)
            song_node = self.song_list.head
            while song_node:
                if os.path.basename(song_node.song.music_file) == song_name:
                    self.song_list.current = song_node
                    self.play_music()
                    break
                song_node = song_node.next

    def play_music(self):
        if self.song_list.current:
            pygame.mixer.music.load(self.song_list.current.song.music_file)
            pygame.mixer.music.play(loops=0)
            self.song_label.config(text=f"Now Playing: {os.path.basename(self.song_list.current.song.music_file)}")
            self.current_song_path = self.song_list.current.song.music_file

    def stop_music(self):
        pygame.mixer.music.stop()
        self.song_label.config(text="")

    def pause_music(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.paused = True

    def play_previous(self):
        if self.song_list.current and self.song_list.current.prev:
            self.song_list.current = self.song_list.current.prev
            self.play_music()

    def play_next(self):
        if self.song_list.current and self.song_list.current.next:
            self.song_list.current = self.song_list.current.next
            self.play_music()

    def update_progress(self):
        if self.song_list.current and pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000
            total_time = MP3(self.song_list.current.song.music_file).info.length
            self.progress_scale.set((current_time / total_time) * 1000)
            self.elapsed_time_label.config(text=self.format_time(current_time))
            self.remaining_time_label.config(text=self.format_time(total_time - current_time))
        self.root.after(1000, self.update_progress)

    @staticmethod
    def format_time(seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{str(seconds).zfill(2)}"

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
