from PIL import Image, ImageDraw, ImageFont

def create_book_cover(title, author, output_path, background_image_path=None):
    # מימדי התמונה
    width, height = 600, 800
    background_color = "white"  # צבע מילוי לרקע שקוף
    title_color = "black"
    author_color = "gray"

    # יצירת רקע לבן בסיסי
    background = Image.new("RGB", (width, height), background_color)

    # הוספת תמונת רקע (אם יש)
    if background_image_path:
        foreground = Image.open(background_image_path).convert("RGBA")
        foreground = foreground.resize((width, height))
        background.paste(foreground, (0, 0), foreground)

    # יצירת שכבה חדשה
    image = background.copy()
    draw = ImageDraw.Draw(image)

    # פונטים
    title_font = ImageFont.truetype("arial.ttf", 32)
    author_font = ImageFont.truetype("arial.ttf", 30)

    # חישוב מיקום הטקסט - מיקום יוגדר בהתאם לאזורים פתוחים
    title_x, title_y = 280, 300  # מיקום כותרת ראשית
    author_x, author_y = width // 2, 3 * height // 4  # מיקום כותב הספר

    # חישוב גבולות טקסט למרכז
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_text_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_text_width) // 2  # מרכז הכותרת

    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_text_width = author_bbox[2] - author_bbox[0]
    author_x = (width - author_text_width) // 2  # מרכז שם הכותב

    # כתיבת הטקסט
    draw.text((title_x, title_y), title, fill=title_color, font=title_font)
    draw.text((author_x, author_y), author, fill=author_color, font=author_font)

    # שמירת התמונה
    image.save(output_path)
    print(f"Book cover saved at {output_path}")

# קריאה לפונקציה
create_book_cover(
    title="My Transparent Cover",
    author="Author Name",
    output_path="book_cover_with_transparency_updated.png",
    background_image_path="background.png",  # שביל לתמונת רקע עם שקיפות
)
