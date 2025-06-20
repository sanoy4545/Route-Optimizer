import tkinter as tk
from tkinter import messagebox
import requests
import threading
from path_optimizer import find_ideal_sequence

try:
    import geocoder
except ImportError:
    geocoder = None

class GooglePlacesAutocompleteEntry(tk.Entry):
    def __init__(self, api_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.listbox = None
        self.suggestions = []
        self.bind("<KeyRelease>", self.on_keyrelease)
        self.bind("<FocusOut>", self.hide_listbox)
        self.selected_place = None

    def on_keyrelease(self, event):
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            return

        typed = self.get()
        if typed == '':
            self.hide_listbox()
            return

        suggestions = self.fetch_suggestions(typed)
        self.show_suggestions(suggestions)

    def fetch_suggestions(self, text):
        url = "https://maps.googleapis.com/maps/api/place/autposite/json"
        params = {
            "input": text,
            "key": self.api_key,
            "types": "establishment",
        }
        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            if data.get("status") == "OK":
                return data.get("predictions", [])
            else:
                return []
        except Exception as e:
            print("Error fetching suggestions:", e)
            return []

    def show_suggestions(self, predictions):
        self.suggestions = predictions
        if not predictions:
            self.hide_listbox()
            return

        if not self.listbox:
            self.listbox = tk.Listbox()
            self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.listbox.delete(0, tk.END)
        for pred in predictions:
            self.listbox.insert(tk.END, pred["description"])

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.listbox.place(x=x, y=y, width=self.winfo_width())

    def hide_listbox(self, event=None):
        if self.listbox:
            self.listbox.place_forget()

    def on_listbox_select(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        place = self.suggestions[index]
        self.selected_place = place

        self.delete(0, tk.END)
        self.insert(0, place["description"])

        self.hide_listbox()

class LocationApp:
    def __init__(self, root, api_key):
        self.api_key = api_key
        self.root = root
        self.root.title("Google Places - Ideal Visiting Sequence")
        self.root.geometry("600x650")

        tk.Label(root, text="Start Location:").pack(pady=5)

        start_frame = tk.Frame(root)
        start_frame.pack(padx=20, fill="x")

        self.start_entry = GooglePlacesAutocompleteEntry(api_key, start_frame)
        self.start_entry.pack(side="left", fill="x", expand=True)

        self.current_loc_btn = tk.Button(start_frame, text="Use My Current Location", command=self.use_current_location)
        self.current_loc_btn.pack(side="left", padx=5)

        tk.Label(root, text="Add Other Locations:").pack(pady=5)
        self.other_entry = GooglePlacesAutocompleteEntry(api_key, root)
        self.other_entry.pack(padx=20, fill="x")

        self.add_btn = tk.Button(root, text="Add Location", command=self.add_location)
        self.add_btn.pack(pady=10)

        self.locations_listbox = tk.Listbox(root)
        self.locations_listbox.pack(padx=20, pady=10, fill="both", expand=True)

        self.submit_btn = tk.Button(root, text="Submit", command=self.submit_locations)
        self.submit_btn.pack(pady=10)

        self.output_box = tk.Text(root, height=15, wrap="none")
        self.output_box.pack(padx=20, pady=10, fill="both", expand=True)

        self.locations = []

    def use_current_location(self):
        if not geocoder:
            messagebox.showerror("Error", "Install geocoder: pip install geocoder")
            return

        def fetch_location():
            self.current_loc_btn.config(state="disabled", text="Getting location...")
            try:
                g = geocoder.ip('me')
                if g.ok and g.latlng:
                    address = self.reverse_geocode(g.latlng)
                    if address:
                        self.start_entry.delete(0, tk.END)
                        self.start_entry.insert(0, address)
                        self.start_entry.selected_place = {"description": address}
                    else:
                        messagebox.showerror("Error", "Could not reverse geocode.")
                else:
                    messagebox.showerror("Error", "Could not get current location.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.current_loc_btn.config(state="normal", text="Use My Current Location")

        threading.Thread(target=fetch_location, daemon=True).start()

    def reverse_geocode(self, latlng):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"latlng": f"{latlng[0]},{latlng[1]}", "key": self.api_key}
        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                return data["results"][0]["formatted_address"]
        except:
            return None
        return None

    def add_location(self):
        place = self.other_entry.selected_place
        if not place:
            messagebox.showwarning("Warning", "Select a valid location from suggestions.")
            return
        desc = place["description"]
        if desc in self.locations:
            messagebox.showinfo("Info", "Location already added.")
            return
        self.locations.append(desc)
        self.locations_listbox.insert(tk.END, desc)
        self.other_entry.delete(0, tk.END)
        self.other_entry.selected_place = None

    def submit_locations(self):
        start_place = self.start_entry.selected_place
        if not start_place:
            messagebox.showwarning("Warning", "Please select a start location.")
            return

        all_places = [start_place["description"]] + self.locations
        dist_matrix = self.get_distance_matrix(all_places)

        if dist_matrix is None:
            messagebox.showerror("Error", "Failed to fetch distance matrix.")
            return

        sequence = find_ideal_sequence(dist_matrix, start=0)
        ordered_places = [all_places[i] for i in sequence]

        result = "Ideal Visiting Sequence:\n\n"
        for idx, place in enumerate(ordered_places):
            result += f"{idx + 1}. {place}\n"

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, result)

    def get_distance_matrix(self, places):
        origins = "|".join(places)
        destinations = "|".join(places)
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origins,
            "destinations": destinations,
            "key": self.api_key,
            "mode": "driving",
            "units": "metric",
        }
        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            if data.get("status") != "OK":
                return None
            matrix = []
            for row in data.get("rows", []):
                distances = []
                for element in row.get("elements", []):
                    if element.get("status") == "OK":
                        distances.append(element["distance"]["value"])
                    else:
                        distances.append(None)
                matrix.append(distances)
            return matrix
        except:
            return None

if __name__ == "__main__":
    API_KEY = "YOUR_API_KEY_HERE"  # Replace with your Google API key
    root = tk.Tk()
    app = LocationApp(root, API_KEY)
    root.mainloop()
