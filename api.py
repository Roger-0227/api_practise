from PIL import Image, ImageTk
import tkinter as tk
import requests, random, io


class MetropolitanApp:
    def __init__(self, base):
        self.api_object_url = (
            "https://collectionapi.metmuseum.org/public/collection/v1/objects"
        )
        self.search_object_url = (
            "https://collectionapi.metmuseum.org/public/collection/v1/search?"
        )
        self.total_num = 0
        self.index_num = 0
        self.canvas_width = 400
        self.canvas_heigth = 400
        self.art_ids = []
        self.art_info = tk.StringVar()

        default_art_id = 5535
        search_frame = tk.Frame(base)
        control_frame = tk.Frame(base)

        self.label_text = tk.StringVar()
        self.label_text.set("Enter keyword and push search button")
        self.label = tk.Label(base, textvariable=self.label_text)
        self.entry = tk.Entry(search_frame)
        self.search_button = tk.Button(
            search_frame, text="Search", command=self.searchArt
        )
        self.random_button = tk.Button(
            control_frame, text="Random", command=self.selectRandom
        )
        self.next_button = tk.Button(control_frame, text="Next", command=self.nextArt)
        self.prev_button = tk.Button(control_frame, text="Prev", command=self.prevArt)

        self.canvas = tk.Canvas(
            base,
            bg="black",
            borderwidth=5,
            relief=tk.RIDGE,
            width=self.canvas_width,
            height=self.canvas_heigth,
        )

        response = self.getArtObject(default_art_id)
        image_url = response["primaryImageSmall"]
        image_pil = Image.open(io.BytesIO(requests.get(image_url).content))
        image_pil = self.resizeArtImage(image_pil)
        self.photo_image = ImageTk.PhotoImage(image_pil)

        self.canvas_number = self.canvas.create_image(
            self.canvas_width / 2 + 5,
            self.canvas_heigth / 2 + 5,
            anchor=tk.CENTER,
            image=self.photo_image,
        )

        self.artInfoArea = tk.Message(
            base, relief="raised", textvariable=self.art_info, width=self.canvas_width
        )
        self.displayArtInfo(response)

        search_frame.pack()
        self.entry.grid(column=0, row=0, pady=10)
        self.search_button.grid(column=1, row=0, padx=10, pady=10)
        self.label.pack()
        self.canvas.pack()

        control_frame.pack()
        self.prev_button.grid(column=0, row=0, padx=50)
        self.random_button.grid(column=1, row=0, padx=50, pady=10)
        self.next_button.grid(column=2, row=0, padx=50, pady=10)
        self.artInfoArea.pack()

    def searchArt(self):
        search_art_url = f"{self.search_object_url}q={self.entry.get()}&hasImages=true"
        response = requests.get(search_art_url)
        response_dict = response.json()

        self.index_num = 0
        self.total_num = response_dict["total"]
        self.art_ids = response_dict["objectIDs"]
        self.displayArt(self.art_ids[0])

    def nextArt(self):
        self.index_num = self.index_num + 1
        if self.index_num > self.total_num - 1:
            self.index_num = 0
        next_art_id = self.art_ids[self.index_num]
        self.displayArt(next_art_id)

    def prevArt(self):
        self.index_num = self.index_num - 1
        if self.index_num < 0:
            self.index_num = self.total_num - 1
        prev_art_id = self.art_ids[self.index_num]
        self.displayArt(prev_art_id)

    def selectRandom(self):
        self.index_num = random.randint(0, (self.total_num - 1))
        art_id = self.art_ids[self.index_num]
        self.displayArt(art_id)

    def getArtObject(self, object_id):
        get_object_url = f"{self.api_object_url}/{str(object_id)}"
        api_response = requests.get(get_object_url)
        return api_response.json()

    def displayArt(self, object_id):
        art_object = self.getArtObject(object_id)
        self.label_text.set(f"{(self.index_num + 1)}/{self.total_num}")
        self.displayArtImage(art_object)
        self.displayArtInfo(art_object)

    def displayArtImage(self, art_object):
        image_url = art_object["primaryImageSmall"]
        image_pil = Image.open(io.BytesIO(requests.get(image_url).content))
        image_pil = self.resizeArtImage(image_pil)
        self.photo_image = ImageTk.PhotoImage(image_pil)
        self.canvas.itemconfig(self.canvas_number, image=self.photo_image)

    def displayArtInfo(self, art_object):
        art_info_text = f"[Title]:{art_object['title']}\n"
        art_info_text += f"[Artist]:{art_object['artistDisplayName']}\n"
        art_info_text += f"[Type]:{art_object['classification']}\n"
        art_info_text += f"[URL]:{art_object['objectURL']}"
        self.art_info.set(art_info_text)

    def resizeArtImage(self, art_image):
        if art_image.width > art_image.height:
            resize_ratio = round(self.canvas_width / art_image.width, 2)
        else:
            resize_ratio = round(self.canvas_heigth / art_image.height, 2)

        return art_image.resize(
            (int(art_image.width * resize_ratio), int(art_image.height * resize_ratio))
        )


base = tk.Tk()
base.title("The MetropolitanApp Museum of Art collection Viewer")
base.geometry("500x700")
app = MetropolitanApp(base)
base.mainloop()
