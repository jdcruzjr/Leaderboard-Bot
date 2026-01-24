"""
Podium image generator for Discord leaderboard bot.
Creates a podium-style image with top 3 players' discord pfps
"""

from PIL import Image, ImageDraw, ImageFont
import requests
import PIL
from io import BytesIO

# TODO: Make 1 and 5 place podiums
    # Adjust draw_podium_blocks function to make stands based on number of places user wants to display
    # Adjust draw_podium_blocks function to make size of stands based on ties
# TODO: Account for ties in the leaderboard
    # Adjust above
    # Adjust add_text_to_podium to label podium stands based on standings (if tie -> label both stands with higher ranking)
# TODO: Add placeholder images when no pfp found
# TODO: Test with various image formats (webp, png, jpg, gif, etc.)
# TODO: Polish code (optimize imports, comments, structure, etc.)

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
    padding = 20
    block_width = (canvas_width - padding * 4) / 3  # 3 blocks with padding in between

    first_height = canvas_height / 1.5
    second_height = canvas_height / 2
    third_height = canvas_height / 2.5

    # Draw 2nd Place (Left block)
    draw_podium_block_rounded_top(
        draw, 
        padding, canvas_height - second_height,
        block_width + padding, canvas_height,
        radius=20,
        fill_color=(192, 192, 192)
    ) # Silver rectangle

    # Draw 1st Place (Middle block)
    draw_podium_block_rounded_top(
        draw, 
        block_width + padding * 2, canvas_height - first_height,
        block_width * 2 + padding * 2, canvas_height,
        radius=20,
        fill_color=(255, 215, 0)
    ) # Gold rectangle

    # Draw 3rd Place (Right block)
    draw_podium_block_rounded_top(
        draw, 
        block_width * 2 + padding * 3, canvas_height - third_height,
        block_width * 3 + padding * 3, canvas_height,
        radius=20,
        fill_color=(205, 127, 50)
    ) # Bronze rectangle

def add_text_to_podium(draw, username, score, position, x, y):
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
    username_font = ImageFont.truetype("arialbd.ttf", 32)

    # Get username text dimensions
    bbox = draw.textbbox((0,0), username_text, font=username_font)
    username_width = bbox[2] - bbox[0]
    username_height = bbox[3] - bbox[1]

    # Center the username at (x, y)
    username_x = x - (username_width / 2)
    username_y = y - (username_height / 2)
    draw.text((username_x, username_y), username_text, font=username_font, fill=(255, 255, 255))

    # Next, add score below username
    score_text = f"{score} pts"
    score_font = ImageFont.truetype("arial.ttf", 20)

    # Get score text dimensions
    bbox = draw.textbbox((0,0), score_text, font=score_font)
    score_width = bbox[2] - bbox[0]
    score_height = bbox[3] - bbox[1]

    # Center the score below username
    score_x = x - (score_width / 2)
    score_y = username_y + username_height + 20  # 10px below username
    draw.text((score_x, score_y), score_text, font=score_font, fill=(255, 255, 255))

    # Finally, add rank below score
    rank_text = str(position)
    rank_font = ImageFont.truetype("arialbd.ttf", 48)

    # Get rank text dimensions
    bbox = draw.textbbox((0,0), rank_text, font=rank_font)
    rank_width = bbox[2] - bbox[0]
    rank_height = bbox[3] - bbox[1]

    # Center the rank below score
    rank_x = x - (rank_width / 2)
    rank_y = score_y + score_height + 30  # 10px below score
    draw.text((rank_x, rank_y), rank_text, font=rank_font, fill=(255, 255, 255))

def add_medal_to_podium(draw, medal, x, y):
    """
    Add a medal emoji above the podium.

    Args:
        draw (ImageDraw): Drawing context
        medal (str): Medal emoji (e.g., "🥇")
        x (int): X coordinate
        y (int): Y coordinate
    """
    medal_font = ImageFont.truetype("seguiemj.ttf", 48)

    bbox = draw.textbbox((0,0), medal, font=medal_font)
    medal_width = bbox[2] - bbox[0]
    medal_height = bbox[3] - bbox[1]

    medal_x = x - (medal_width / 2)
    medal_y = y - (medal_height / 2)

    draw.text((medal_x, medal_y), medal, font=medal_font, embedded_color=True)

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
    PFP_SIZE = 150
    padding = 20
    block_width = (CANVAS_WIDTH - padding * 4) / 3

    # Get top 3 players
    top_players = leaderboard_heap[:3]
    for i in range(len(top_players)):
        top_players[i] = (-top_players[i][0], top_players[i][1], i + 1)  # Convert score back to positive

    canvas = create_podium_base(CANVAS_WIDTH, CANVAS_HEIGHT, (54, 69, 79)) # or (51, 51, 51) charcoal gray
    
    draw = ImageDraw.Draw(canvas)
    draw_podium_blocks(draw, CANVAS_WIDTH, CANVAS_HEIGHT)

    disc_pfp = []
    for player in top_players:
        score, player_name, position = player
        member = member_objects.get(player_name)
        if member:
            pfp_url = str(member.avatar.url)
            pfp_image = download_pfp(pfp_url)
            if pfp_image:
                circular_pfp = create_circular_pfp(pfp_image, (PFP_SIZE, PFP_SIZE))
                disc_pfp.append(circular_pfp)
            else: # Failed to download pfp
                disc_pfp.append(None)
        else: # Member not found
            disc_pfp.append(None)

    medal_img = ""
    
    first_block_center = (CANVAS_WIDTH / 2)
    first_x = int(first_block_center - (PFP_SIZE / 2))
    first_y = int(CANVAS_HEIGHT - (CANVAS_HEIGHT / 1.5) - PFP_SIZE - 20)
    canvas.paste(disc_pfp[0], (first_x, first_y), disc_pfp[0]) if disc_pfp[0] else None

    second_block_center = (block_width / 2) + padding
    second_x = int(second_block_center - (PFP_SIZE / 2))
    second_y = int(CANVAS_HEIGHT - (CANVAS_HEIGHT / 2) - PFP_SIZE - 20)
    canvas.paste(disc_pfp[1], (second_x, second_y), disc_pfp[1]) if disc_pfp[1] else None

    third_block_center = (CANVAS_WIDTH - (block_width / 2) - padding)
    third_x = int(third_block_center - (PFP_SIZE / 2))
    third_y = int(CANVAS_HEIGHT - (CANVAS_HEIGHT / 2.5) - PFP_SIZE - 20)
    canvas.paste(disc_pfp[2], (third_x, third_y), disc_pfp[2]) if disc_pfp[2] else None

    first_text_y = (CANVAS_HEIGHT - (CANVAS_HEIGHT / 1.5)) + 50
    add_text_to_podium(draw, top_players[0][1], top_players[0][0], 1, first_block_center, first_text_y)

    second_text_y = (CANVAS_HEIGHT - (CANVAS_HEIGHT / 2)) + 50
    add_text_to_podium(draw, top_players[1][1], top_players[1][0], 2, second_block_center, second_text_y)

    third_text_y = (CANVAS_HEIGHT - (CANVAS_HEIGHT / 2.5)) + 50
    add_text_to_podium(draw, top_players[2][1], top_players[2][0], 3, third_block_center, third_text_y)

    add_medal_to_podium(draw, "🥇", first_block_center, first_y - 40)
    add_medal_to_podium(draw, "🥈", second_block_center, second_y - 40)
    add_medal_to_podium(draw, "🥉", third_block_center, third_y - 40)

    canvas.save(output_path)

    return output_path

# For testing purposes
if __name__ == "__main__":
    test_url = "https://cdn.discordapp.com/avatars/224609705555656705/f5694ee8f4bde9edc775cd9a8cc8a822.webp?size=80" # Teemo pfp (from azul)

    test_heap = [(-500, "Player1"), (-450, "Player2"), (-400, "Player3")]

    class MockMember:
        def __init__(self, url):
            self.avatar = type('obj', (object,), {'url': url})()
    
    test_member_objects = {
        "Player1": MockMember(test_url),
        "Player2": MockMember(test_url),
        "Player3": MockMember(test_url)
    }

    result = generate_podium_image(test_heap, test_member_objects, "test_podium.png")
    print(f"Podium image saved to: {result}")



