from PIL import Image, ImageDraw, ImageFont
import os, json
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
}



def generate_tool_sequence_image(solved_data, output_file="tools_sequence_visual.png"):
    image_width = 500
    header_height = 32
    row_height = 40
    margin = 32
    font_size = 20
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    operation_images = load_operation_images()
    operation_image_size = list(operation_images.values())[0].size
    step_spacing = operation_image_size[0] + 2

    total_rows = sum(len(tools) + 1 for tools in solved_data.values())
    total_height = total_rows * row_height + header_height + margin * 2


    img = Image.new("RGBA", (image_width, total_height), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()


    y_offset = margin
    tool_canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))

    for metal, tools in solved_data.items():
        draw.rectangle(
            [16, y_offset, image_width - 16, y_offset + row_height],
            fill="#dddddd",
            outline="black"
        )
        draw.text(
            (32, y_offset + row_height // 2),
            metals[metal],
            fill="black",
            anchor="lm",
            font=font
        )
        y_offset += row_height

        for tool, sequence in tools.items():
            tool_img_path =  f"icons/items/metal/{tool.lower()}/{metal.lower()}.png"

            if metal in specialImages and tool in specialImages[metal]:
                tool_img_path = specialImages[metal][tool]
            def add_image(tool_img_path):
                tool_img = Image.open(tool_img_path).convert("RGBA").resize((32, 32), Image.Resampling.NEAREST)
                tool_position = (margin * 2 - 16, y_offset + row_height // 4)
                tool_canvas.paste(tool_img, tool_position, tool_img)
            if os.path.exists(tool_img_path):
               add_image(tool_img_path)
            else:
                draw.text(
                    (margin * 2, y_offset + row_height // 4 + 16),
                    tool,
                    fill="black",
                    anchor="mm",
                    font=font
                )

            x_offset = margin * 4
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

        y_offset += 8

    img = Image.alpha_composite(img, tool_canvas)
    img.save(output_file)

if __name__ == "__main__":
    solved_data_example = getAllToolsSolved()
    
    with open("solved_data.json", "w") as f:
        f.write(json.dumps(solved_data_example))

    generate_tool_sequence_image(solved_data_example)
