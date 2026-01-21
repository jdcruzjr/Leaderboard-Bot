"""
Podium image generator for Discord leaderboard bot.
Creates a podium-style image with top 3 players' discord pfps
"""

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# TODO: Make 1, 3, and 5 place podiums
    # Adjust draw_podium_blocks function to make stands based on number of places user wants to display
    # Adjust draw_podium_blocks function to make size of stands based on ties
# TODO: Account for ties in the leaderboard
    # Adjust above
    # Adjust add_text_to_podium to label podium stands based on standings (if tie -> label both stands with higher ranking)

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
    canvas = Image.new("RGBA", (width, height), background_color)

    return canvas

def draw_podium_block_rounded_top(draw, x1, y1, x2, y2, radius, fill_color):
    """
    Helper method for draw_podium_blocks
    
    Draw a rectangle with only top corners rounded
    """
    # Draw the main rectangle (no rounded corners)
    draw.rectangle([(x1, y1 + radius), (x2, y2)], fill=fill_color)
    
    # Draw rounded top-left corner
    draw.pieslice([(x1, y1), (x1 + radius*2, y1 + radius*2)], 
                  start=180, end=270, fill=fill_color)
    
    # Draw rounded top-right corner  
    draw.pieslice([(x2 - radius*2, y1), (x2, y1 + radius*2)], 
                  start=270, end=360, fill=fill_color)
    
    # Fill in the top middle section
    draw.rectangle([(x1 + radius, y1), (x2 - radius, y1 + radius)], fill=fill_color)

def draw_podium_blocks(draw, canvas_width, canvas_height):
    """
    Draw the podium blocks (rectangle) for 1st, 2nd, 3rd place.

    Args:
        draw (ImageDraw): Drawing context
        canvas_width (int): Width of canvas
        canvas_height (int): Height of canvas
    """
    block_width = canvas_width / 3

    first_height = 350
    second_height = 250
    third_height = 200

    # Draw 2nd Place (Left block)
    draw_podium_block_rounded_top(
        draw, 
        0, canvas_height - second_height,
        block_width, canvas_height,
        radius=20,
        fill_color=(192, 192, 192)
    ) # Silver rectangle

    # Draw 1st Place (Middle block)
    draw_podium_block_rounded_top(
        draw, 
        block_width, canvas_height - first_height,
        block_width * 2, canvas_height,
        radius=20,
        fill_color=(255, 215, 0)
    ) # Gold rectangle

    # Draw 3rd Place (Right block)
    draw_podium_block_rounded_top(
        draw, 
        block_width * 2, canvas_height - third_height,
        canvas_width, canvas_height,
        radius=20,
        fill_color=(205, 127, 50)
    ) # Bronze rectangle

def add_text_to_podium(draw, username, score, position, x, y, font):
    """
    Add text (username, score, rank) to the podium.
    
    Args:
        draw (ImageDraw): Drawing context
        username (str): Player's username
        score (int): Player's score
        position (int): Rank (1, 2, or 3)
        x (int): X coordinate for text
        y (int): Y coordinate for text
        font (ImageFont): Font to use
    """
    # Start with username (and then work way down)
    username_text = username

    # Get username text dimensions
    bbox = draw.textbbox((0,0), username_text, font=font)
    username_width = bbox[2] - bbox[0]
    username_height = bbox[3] - bbox[1]

    # Center the username at (x, y)
    username_x = x - (username_width / 2)
    username_y = y - (username_height / 2)
    draw.text((username_x, username_y), username_text, font=font, fill=(0,0,0))

    # Next, add score below username
    score_text = f"{score} pts"

    # Get score text dimensions
    bbox = draw.textbbox((0,0), score_text, font=font)
    score_width = bbox[2] - bbox[0]
    score_height = bbox[3] - bbox[1]

    # Center the score below username
    score_x = x - (score_width / 2)
    score_y = username_y + username_height + 10  # 10px below username
    draw.text((score_x, score_y), score_text, font=font, fill=(0,0,0))

    # Finally, add rank below score
    rank_text = str(position)

    # Get rank text dimensions
    bbox = draw.textbbox((0,0), rank_text, font=font)
    rank_width = bbox[2] - bbox[0]
    rank_height = bbox[3] - bbox[1]

    # Center the rank below score
    rank_x = x - (rank_width / 2)
    rank_y = score_y + score_height + 20  # 10px below score
    draw.text((rank_x, rank_y), rank_text, font=font, fill=(0,0,0))

def generate_podium_image(leaderboard_heap, member_objects, output_path="podium.png"):
    """
    Main function to generate the complete podium image.
    
    Args:
        leaderboard_heap (list): List of tuples with player data
                           [(-score, player_name), ...]
        member_objects (list): Dictionary mapping player_name -> discord.Member object
        output_path (str): Where to save the final image
        
    Returns:
        str: Path to the saved image
    """
    #TODO: What if less than 3 players? (slicing handles this gracefully) What if ties? What if more than 3 players?
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 800

    # Get top 3 players
    top_players = leaderboard_heap[:3]
    for i in range(len(top_players)):
        top_players[i] = (-top_players[i][0], top_players[i][1], i + 1)  # Convert score back to positive

    # Create canvas and draw podium blocks
    canvas = create_podium_base(CANVAS_WIDTH, CANVAS_HEIGHT, (240, 240, 250))
    canvas.show()

# For testing purposes
if __name__ == "__main__":
    test_url = "https://cdn.discordapp.com/avatars/224609705555656705/f5694ee8f4bde9edc775cd9a8cc8a822.webp?size=80" # Teemo pfp (from azul)

    pfp = download_pfp(test_url)
    if pfp:
        print("Avatar downloaded successfully!")
        print(f"Size: {pfp.size}")  # Shows (width, height)
        # pfp.show()  # Opens the image in your default image viewer
    else:
        print("Failed to download avatar")

    circular_pfp = create_circular_pfp(pfp, (150, 150))

    # circular_pfp.show()

    canvas_width = 800
    canvas_height = 800

    canvas = create_podium_base(canvas_width, canvas_height, (240, 240, 250))

    draw = ImageDraw.Draw(canvas)
    draw_podium_blocks(draw, canvas_width, canvas_height)

    font_big = ImageFont.truetype("arialbd.ttf", 32)
    first_height = 350
    second_height = 250
    third_height = 200
    block_width = canvas_width // 3
    
    # Calculate center of 1st place block
    first_x = block_width * 1.5  # Center of middle block
    first_y = (canvas_height - first_height) + 75  # 100px from top of block

    # Calculate center of 2nd place block
    second_x = block_width * 0.5
    second_y = (canvas_height - second_height) + 75

    # Calculate center of 3rd place block
    third_x = block_width * 2.5
    third_y = (canvas_height - third_height) + 75

    add_text_to_podium(draw, "Player1", 4, 1, first_x, first_y, font_big)
    add_text_to_podium(draw, "Player2", 2, 2, second_x, second_y, font_big)
    add_text_to_podium(draw, "Player3", 1, 3, third_x, third_y, font_big)

    # canvas.show()

    generate_podium_image([(-500, "Player1"), (-450, "Player2"), (-400, "Player3")], {}, output_path="test_podium.png")



