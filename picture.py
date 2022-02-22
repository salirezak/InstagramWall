from PIL import Image, ImageFont, ImageDraw
import arabic_reshaper, io, random

BG_COLORS = ['#0079b0', '#ff7928', '#009d3e', '#e3202c',
             '#946ab8', '#91554d', '#eb77bd', '#7e7e7e', '#bfb93f', '#00becd']

pic_width, pic_height = 1080, 1920
pic_width, pic_height = 2160, 3840
font_size, line_space = int(pic_width/18), pic_height/110
x, y = pic_width/7.5, (pic_height/2)-(pic_height/20)
txt_width, txt_height  = pic_width-(3*x), pic_height/2

def generate_text(text, font_path="static/font/Vazir-Medium.ttf", font_size=font_size, line_space=line_space, txt_width=txt_width, txt_height=txt_height):
    #create a font object to use getsize method
    font = ImageFont.truetype(font_path, font_size, encoding='unic')
    #correct shap of arabic & persain chars
    text = arabic_reshaper.reshape(text)
    #separate lines of text to keep input lines
    plines = list(map(lambda l: l.strip(), text.strip().split('\n')))
    #separate words of each line
    plines_words = [list(map(lambda w: w+" ", pline.split())) for pline in plines]

    lines_words = []
    lines = []

    #breaking long words
    for pline_words in plines_words:
        line_words = []
        while len(pline_words) != 0:
            word = pline_words[0]
            #long word
            if font.getsize(word)[0] > txt_width:
                #break word
                for i in range(len(word)):
                    check_word, pre_word, after_word = word[:i+2], word[:i+1], word[i+1:]
                    if font.getsize(check_word)[0] > txt_width:
                        line_words.append(pre_word)
                        pline_words[0] = after_word
                        break
            #normal word
            else:
                line_words.append(word)
                del pline_words[0], word
        lines_words.append(line_words)

    #breaking long lines
    for line_words in lines_words:
        while len(line_words) != 0:
            for i in range(len(line_words)):
                check_line = (''.join(line_words[:i+2])).strip()
                main_line = (''.join(line_words[:i+1])).strip()
                #last line
                if i == len(line_words)-1 and font.getsize(main_line)[0] < txt_width:
                    lines.append(main_line)

                    lines_height = font.getsize_multiline('\n'.join(lines).strip(), None, line_space)[1]
                    if txt_height < lines_height:
                        return False

                    del line_words[:i+1], check_line, main_line, lines_height
                    break
                #long line
                elif font.getsize(check_line)[0] > txt_width:
                    lines.append(main_line)

                    lines_height = font.getsize_multiline('\n'.join(lines).strip(), None, line_space)[1]
                    if txt_height < lines_height:
                        return False

                    del line_words[:i+1], check_line, main_line
                    break

    text = '\n'.join(lines).strip()

    lines_height = font.getsize_multiline(text, None, line_space)[1]
    if txt_height < lines_height:
        return False

    return text

def  generate_pic(text, font_path="static/font/Vazir-Medium.ttf", font_size=font_size, line_space=line_space, pic_width=pic_width, pic_height=pic_height, x=x, y=y, bg_color='#bfbfbf', txt_color='#ffffff'):
	font = ImageFont.truetype(font_path, font_size, encoding='unic')
	image = Image.new('RGB', (pic_width, pic_height), bg_color)

	draw = ImageDraw.Draw(image)
	draw.multiline_text((x, y), text, txt_color, font, 'lm', line_space)

	#image.save('test.png', format="PNG")
	tmp = io.BytesIO()
	image.save(tmp, format="PNG")
	return tmp.getvalue()

def bg_color():
    return random.choice([
        '#0079b0', '#ff7928', '#009d3e', '#e3202c',
        '#946ab8', '#91554d', '#eb77bd', '#7e7e7e',
        '#bfb93f', '#00becd'
    ])