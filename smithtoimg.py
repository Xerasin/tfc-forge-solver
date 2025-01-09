from PIL import Image, ImageDraw, ImageFont
import os
from smithing import getAllToolsSolved, compress_sequence, metals
def load_operation_images():
    operation_images = {
        "S":  Image.open("icons/shrink.png"),
        "B":  Image.open("icons/bend.png"),
        "U":  Image.open("icons/upset.png"),
        "P":  Image.open("icons/punch.png"),
        "LH": Image.open("icons/light_hit.png"),
        "MH": Image.open("icons/medium_hit.png"),
        "HH": Image.open("icons/hard_hit.png"),
        "D":  Image.open("icons/draw.png")
    }
    return operation_images

specialImages = {
    "wrought_iron": {
        "refined_bloom": "icons/items/refined.png"
    }
}



def generate_tool_sequence_image(solved_data, output_file="tools_sequence_visual.png"):
    # Constants
    image_width = 500
    header_height = 32
    row_height = 40
    margin = 32
    font_size = 20
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust based on your system

    # Load operation images
    operation_images = load_operation_images()
    operation_image_size = list(operation_images.values())[0].size
    step_spacing = operation_image_size[0] + 2

    # Calculate total image height
    total_rows = sum(len(tools) + 1 for tools in solved_data.values())  # +1 for metal headers
    total_height = total_rows * row_height + header_height + margin * 2

    # Create image canvas
    img = Image.new("RGBA", (image_width, total_height), color="white")
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Draw header
    y_offset = margin
    tool_canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))

    # Draw metal sections
    for metal, tools in solved_data.items():
        # Draw metal header
        draw.rectangle(
            [margin, y_offset, image_width - margin, y_offset + row_height],
            fill="#dddddd",
            outline="black"
        )
        draw.text(
            (margin * 2, y_offset + row_height // 2),
            metals[metal],
            fill="black",
            anchor="lm",
            font=font
        )
        y_offset += row_height
        
        
        # Draw tools and their sequences
        for tool, sequence in tools.items():
            tool_img_path =  f"icons/items/metal/{tool.lower()}/{metal.lower()}.png"

            if metal in specialImages and tool in specialImages[metal]:
                tool_img_path = specialImages[metal][tool]

            if os.path.exists(tool_img_path):
                tool_img = Image.open(tool_img_path).convert("RGBA").resize((32, 32), Image.Resampling.NEAREST)
                tool_position = (margin * 2, y_offset + row_height // 4)
                tool_canvas.paste(tool_img, tool_position, tool_img)
            else:
                draw.text(
                    (margin * 2, y_offset + row_height // 4 + 16),
                    tool,
                    fill="black",
                    anchor="lm",
                    font=font
                )

            # Draw operation images for the sequence
            x_offset = margin * 5
            sequence = compress_sequence(sequence)
            for step, count in sequence:
                operation_img = operation_images[step]
                tool_canvas.paste(operation_img, (x_offset, y_offset + row_height // 4))
                x_offset += step_spacing

                draw.text(
                    (x_offset, y_offset + row_height // 4 + 16),
                    f"x {count}",
                    fill="black",
                    anchor="lm",
                    font=font
                )
                x_offset += 16


            y_offset += row_height

        y_offset += 5

    img = Image.alpha_composite(img, tool_canvas)
    # Save the image
    img.save(output_file)
    print(f"Image saved as {output_file}")

# Example Solved Data
solved_data_example = getAllToolsSolved()

# Generate the image
generate_tool_sequence_image(solved_data_example)
