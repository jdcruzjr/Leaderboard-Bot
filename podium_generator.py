"""
Podium image generator for Discord leaderboard bot.
Creates a podium-style image with top 3 players' discord pfps
"""

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def download_pfp(pfp_url):
    """
    Download a Discord pfp from URL.

    Args:
        pfp_url (str): URL of the Discord profile picture

    Returns:
        Image: PIL Image object of the pfp
    """
    try:
        response = requests.get(pfp_url) # Fetching image from URL
        image_data = response.content # Getting raw bytes
        image_bytes = BytesIO(image_data) # Wrap in BytesIO (so Pillow can read it)
        image = Image.open(image_bytes) # Open with Pillow

        return image
    except Exception as e:
        print(f"Error downloading avatar: {e}")
        return None

def create_circular_pfp(image, size):
    """
    Convert a square pfp into a circular one with given size.

    Args:
        image (Image): PIL Image object
        size (tuple): (width, height) for the circular pfp

    Returns:
        Image: Circular pgp image with transparency
    """
    resized_image = image.resize(size)
    resized_image = resized_image.convert("RGBA") # Adds a transparency layer (alpha channel)
    
    mask = Image.new('L', size, 0) # Create a mask (a black square = "hide everything"/fully transparent)
    draw = ImageDraw.Draw(mask)  # Add white circle to the mask (white = "fully visible")
    draw.ellipse((0, 0, size[0], size[1]), fill = 255) # White circle

    resized_image.putalpha(mask) # Mask becomes alpha channel (sort of like cookie cutter)

    return resized_image


def create_podium_base(width, height, background_color):
    """
    Create the base canvas for the podium image.

    Args:
        width (int): Width of the canvas
        height (int): Height of the canvas
        background_color (tuple): RGB color tuple

    Returns:
        Image: Blank canvas image
    """
    pass

def draw_podium_blocks(draw, canvas_width, canvas_height):
    """
    Draw the podium blocks (rectangle) for 1st, 2nd, 3rd place.

    Args:
        draw (ImageDraw): Drawing context
        canvas_width (int): Width of canvas
        canvas_height (int): Height of canvas
    """
    pass

def add_text_to_podium(draw, username, position, x, y, font):
    """
    Add text (username, rank, score) to the podium.
    
    Args:
        draw (ImageDraw): Drawing context
        username (str): Player's username
        position (int): Rank (1, 2, or 3)
        x (int): X coordinate for text
        y (int): Y coordinate for text
        font (ImageFont): Font to use
    """
    pass


def generate_podium_image(top_players, output_path="podium.png"):
    """
    Main function to generate the complete podium image.
    
    Args:
        top_players (list): List of dicts with player data
                           [{username: str, avatar_url: str, score: int}, ...]
        output_path (str): Where to save the final image
        
    Returns:
        str: Path to the saved image
    """
    pass 

# For testing purposes
if __name__ == "__main__":
    test_url = "https://cdn.discordapp.com/avatars/224609705555656705/f5694ee8f4bde9edc775cd9a8cc8a822.webp?size=80" # Teemo pfp (from azul)

    pfp = download_pfp(test_url)
    if pfp:
        print("Avatar downloaded successfully!")
        print(f"Size: {pfp.size}")  # Shows (width, height)
        pfp.show()  # Opens the image in your default image viewer
    else:
        print("Failed to download avatar")

    circular_pfp = create_circular_pfp(pfp, (150, 150))

    circular_pfp.show()
