from PIL import Image, ImageDraw, ImageFont
import re
with open('nguyenlieu/listcolor.txt', 'r') as f:
    list_color = f.read().split('\n')
list_all = []
for item in list_color:
    if item.strip() == "":
        continue
    else:
        name,code = item.split("|")
        list_all.append([name.strip(),code.strip()])
def parse_selection(selection):
    selection = str(selection)

    pattern = r"Selection\(start=(\d+), end=(\d+), text='([^']+)', labels=\['([^']+)'\]\)"
    match = re.match(pattern, selection)
    for item in list_all:
        if match:
            if item[0] == match.group(4):
                return {
                    "start": int(match.group(1)),
                    "end": int(match.group(2)),
                    "text": match.group(3),
                    "color": item[1]
                }
    if match:
        return {
            "start": int(match.group(1)),
            "end": int(match.group(2)),
            "text": match.group(3),
            "color": match.group(4)
        }
    return None
def xu_ly_text(input_list,base_text,color):

    list_phan_mau = [parse_selection(item) for item in input_list]
    list_text_sorted = sorted(list_phan_mau, key=lambda x: x['start'])

    new_parts = []
    start = 0
    for part in list_text_sorted:
        if start < part['start']:
            new_parts.append({
                'start': start,
                'end': part['start'] - 1,
                'text': base_text[start:part['start']],
                'color': color
            })
        start = part['end']

    if start < len(base_text):  # Kiểm tra và thêm phần cuối cùng của văn bản nếu cần
        new_parts.append({
            'start': start,
            'end': len(base_text) - 1,
            'text': base_text[start:],
            'color': color
        })

    combined_list = list_text_sorted + new_parts
    final_list = sorted(combined_list, key=lambda x: x['start'])
    return final_list

def draw_text(input_list,base_text,color, image_width, image_height, font_size, font, alignment, khoang_cach_dong,start_text_x=0,start_text_y=10):
    # alignment = "left"

    elements = xu_ly_text(input_list,base_text,color)
    x = start_text_x
    y = 10
    font = ImageFont.truetype(f"nguyenlieu/font/{font}", font_size)
    image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    list_word = []
    for element in elements:
        words = element['text'].split(' ')
        color = tuple(int(element['color'][i:i + 2], 16) for i in (1, 3, 5))
        for word in words:
            if word != "":
                list_word.append((word, color))

    list_dong = []
    list_tamthoi = []
    word_height = 0  # Khởi tạo giá trị ban đầu cho word_height

    for word, color in list_word:
        word_width, word_height = draw.textsize(word + " ", font=font)
        if x + word_width > image_width and list_tamthoi:  # Check if word exceeds the line width
            if alignment == 'center':
                vitribatdau = (image_width - x) / 2
            elif alignment == 'lelf':
                vitribatdau = start_text_x
            elif alignment == 'right':
                vitribatdau = image_width - x
            else:
                vitribatdau = start_text_x
            list_dong.append((list_tamthoi, y, vitribatdau))
            list_tamthoi = []
            x = 0
            y += word_height + khoang_cach_dong
        list_tamthoi.append((word, color))
        x += word_width
    if list_tamthoi:
        if alignment == 'center':
            vitribatdau = (image_width - x) / 2
        elif alignment == 'lelf':
            vitribatdau = start_text_x
        elif alignment == 'right':
            vitribatdau = image_width - x
        else:
            vitribatdau = start_text_x
        list_dong.append((list_tamthoi, y, vitribatdau))
    for list_tamthoi, y, vitribatdau in list_dong:
        x = vitribatdau
        for word, color in list_tamthoi:
            word_width, _ = draw.textsize(word + " ", font=font)
            draw.text((x, y), word, fill=color, font=font)
            x += word_width
    return image