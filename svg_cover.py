import svgwrite

# יצירת אובייקט SVG
dwg = svgwrite.Drawing('book_cover.svg', size=('600px', '900px'))

# הגדרת תמונה ברקע (אם התמונה נמצאת באותו תיק)
background_image_path = "background.png"  # שנה את הנתיב לתמונה שלך
dwg.add(dwg.image(href=background_image_path, insert=(0, 0), size=('600px', '900px')))

# הוספת כותרת
dwg.add(dwg.text('שם הספר', insert=(300, 100), text_anchor="middle", font_size="50px", fill="black"))

# הוספת שם מחבר
dwg.add(dwg.text('שם המחבר', insert=(300, 780), text_anchor="middle", font_size="20px", fill="black"))

# הוספת תמונה (לדוגמה, תמונה קטנה שממוקמת במרכז)
book_image_path = 'book_image.png'  # שנה את הנתיב לתמונה שלך
dwg.add(dwg.image(href=book_image_path, insert=(150, 300), size=('300px', '400px')))

# שמירת קובץ ה-SVG
dwg.save()

print("הקובץ נוצר בהצלחה!")
