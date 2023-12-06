from PIL import Image, ImageDraw, ImageFont
import datetime
import qrcode
# Load the template image
template_path = "1.png"
template_image = Image.open(template_path)

# Create a drawing object
draw = ImageDraw.Draw(template_image)

# Define the font properties
font_path = "arial.ttf"  # Path to the font file
font_size = 46
font = ImageFont.truetype(font_path, font_size)

# Define the text fields
fields = {
    "rollno": "21H71A5449",
    "branch": "AIDS",
    "date_month": datetime.datetime.now().strftime("%B %d, %Y"),
}

# Define the position for each field
positions = {
    "rollno": (324, 1116),
    "branch": (1105, 1116),
    "date_month": (678, 1444),
}

# Set the color of the text
text_color = (255, 255, 255)  # RGB color (white in this example)

date_pos=(256, 1624)
date_v=datetime.datetime.now().strftime("%d-%m-%Y")
draw.text(date_pos,date_v,fill=text_color,font=ImageFont.truetype(font_path, 56),align=['center'])

name_pos=(707,940)
name="Satish tyfhh Yadlapalli"
text_width, text_height = draw.textsize(name, font=ImageFont.truetype(font_path, 70))
name_pos = (name_pos[0] - text_width / 2, name_pos[1] - text_height / 2)
draw.text(name_pos,name,fill=text_color,font=ImageFont.truetype(font_path, 70),align='center')


# Place the text fields on the image
for field, position in positions.items():
    text = fields[field]
    draw.text(position, text, font=font, fill=text_color)


url = "https://www.example.com"  # Replace with your desired URL
qr = qrcode.QRCode(version=1, box_size=10, border=1)
qr.add_data(url)
qr.make(fit=True)
qr_image = qr.make_image(fill_color="black", back_color="white")

# Resize the QR code to fit in the template
qr_image = qr_image.resize((160, 160))
template_image.paste(qr_image, (630, 1760))
# Save the modified image
output_path = "output.png"
template_image.save(output_path)