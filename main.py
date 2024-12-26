import urllib.request
import xml.etree.ElementTree as ET
import vlc
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.core.window import Window

# Set the background color to orange
Window.clearcolor = (1, 0.647, 0, 1)  # Orange color

# A dictionary to map human-friendly names to stream URLs or .asx file links
streams = {
    "Florida ABC": "https://amg00327-coxmediagroup-wftvbreaking-ono-hec7b.amagi.tv/playlist/amg00327-coxmediagroup-wftvbreaking-ono/playlist.m3u8",
    "Florida CBS": "https://cbsn-mia.cbsnstream.cbsnews.com/out/v1/ac174b7938264d24ae27e56f6584bca0/master.m3u8",
    "New-York ABC": "https://content.uplynk.com/channel/ext/72750b711f704e4a94b5cfe6dc99f5e1/wabc_24x7_news.m3u8",
    "New-York CBS": "https://cbsn-ny.cbsnstream.cbsnews.com/out/v1/ec3897d58a9b45129a77d67aa247d136/master.m3u8"
}

class MediaPlayer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.label = Label(text="Select a stream to play:", font_size="20sp", color=(0, 0, 0, 1))  # Black text
        self.add_widget(self.label)

        # Add buttons for each stream with green background and black text
        for name, url in streams.items():
            btn = Button(text=name, size_hint_y=None, height=50, background_normal='', background_color=(0, 1, 0, 1), color=(0, 0, 0, 1))  # Green background, black text
            btn.bind(on_press=lambda instance, url=url: self.play_stream(url))
            self.add_widget(btn)

        # Initialize VLC player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

    def play_stream(self, url):
        if url.endswith(".asx"):
            # Parse the .asx file to get the actual stream URL
            try:
                self.label.text = "Fetching stream..."
                stream_url = self.get_stream_from_asx(url)
                if stream_url:
                    self.start_vlc_player(stream_url)
                else:
                    raise Exception("No valid stream URL found in the .asx file.")
            except Exception as e:
                Logger.error(f"Error fetching .asx stream: {e}")
                self.label.text = "Error: Unable to fetch the stream. Check the .asx file!"
        else:
            # Play the stream directly
            self.start_vlc_player(url)

    def start_vlc_player(self, stream_url):
        try:
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.play()

            # Set VLC player to fullscreen
            self.vlc_player.set_fullscreen(True)

            self.label.text = f"Playing: {stream_url}"
        except Exception as e:
            Logger.error(f"VLC Player Error: {e}")
            self.label.text = "Error: Unable to play the stream!"

    @staticmethod
    def get_stream_from_asx(asx_url):
        # Download the .asx file using urllib
        try:
            with urllib.request.urlopen(asx_url) as response:
                asx_data = response.read()
                # Parse the .asx file as XML
                root = ET.fromstring(asx_data)
                for ref in root.findall(".//{*}ref"):  # Look for <ref> tags
                    href = ref.get("href")
                    if href:  # Return the first valid URL
                        return href
        except Exception as e:
            Logger.error(f"Error downloading or parsing .asx file: {e}")
            return None

        return None  # No valid URL found

class MediaPlayerApp(App):
    def build(self):
        return MediaPlayer()

if __name__ == "__main__":
    MediaPlayerApp().run()
