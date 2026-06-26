import base64
import struct
import PIL
from PIL import Image, ImageOps, ImageChops, ImageDraw, ImageFont
from io import BytesIO

class Renderer:
    printerWidth = 384

    def trimImage(self, im):
        bg = PIL.Image.new(im.mode, im.size, (255,255,255))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0)
        bbox = diff.getbbox()
        if bbox:
            return im.crop((bbox[0],bbox[1],bbox[2],bbox[3]+10)) # don't cut off the end of the image

    # TODO: UPDATE TO INCLUDE IMAGE
    def create_text(self, text, font_name="Lucon.ttf", font_size=32):
        img = PIL.Image.new('RGB', (self.printerWidth, 5000), color = (255, 255, 255))
        font = ImageFont.truetype(font_name, font_size)

        d = ImageDraw.Draw(img)
        lines = []
        for line in text.splitlines():
            lines.append(self.get_wrapped_text(line, font, self.printerWidth))
        lines = "\n".join(lines)
        d.text((0,0), lines, fill=(0,0,0), font=font)
        return self.trimImage(img)

    def create_attachment(self, data):
        if "," in data:
            data = data.split(",")[1]

        image_bytes = base64.b64decode(data)

        return Image.open(BytesIO(image_bytes))

    def createBody(self, message):
        text = None
        image = None
        if (message["msg"] != ""):
            text_raw = self.create_text(message["msg"])
            text = self.processImage(text_raw)

        if (message["img"] != ""):
            image_raw = self.create_attachment(message["img"])
            image = self.processImage(image_raw)

        textHeight = text.height if text is not None else 0
        imgHeight = image.height if image is not None else 0
        totalHeight = textHeight + imgHeight

        new_im = Image.new('1', (self.printerWidth, totalHeight))

        if (image is not None):
            new_im.paste(image, (0,0))
        if (text is not None):
            new_im.paste(text, (0, imgHeight))
        return new_im



    def get_wrapped_text(self, text: str, font: PIL.ImageFont.ImageFont,
                         line_length: int):
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)


    def processImage(self, im):
        if im.width > self.printerWidth:
            # image is wider than printer resolution; scale it down proportionately
            height = int(im.height * (self.printerWidth / im.width))
            im = im.resize((self.printerWidth, height))

        if im.width < self.printerWidth:
            # image is narrower than printer resolution; pad it out with white pixels
            padded_image = PIL.Image.new("1", (self.printerWidth, im.height), 1)
            padded_image.paste(im)
            im = padded_image

        im = im.rotate(180) #print it so it looks right when spewing out of the mouth

        # if image is not 1-bit, convert it
        if im.mode != '1':
            im = im.convert('1')


        # if image width is not a multiple of 8 pixels, fix that
        if im.size[0] % 8:
            im2 = Image.new('1', (im.size[0] + 8 - im.size[0] % 8,
                                  im.size[1]), 'white')
            im2.paste(im, (0, 0))
            im = im2



        # Invert image, via greyscale for compatibility
        #  (no, I don't know why I need to do this)
        im = ImageOps.invert(im.convert('L'))
        # ... and now convert back to single bit
        im = im.convert('1')
        return im

    def getBuffer(self, im):
        buf = b''.join((bytearray(b'\x1d\x76\x30\x00'),
                        struct.pack('2B', int(im.size[0] / 8 % 256),
                                    int(im.size[0] / 8 / 256)),
                        struct.pack('2B', int(im.size[1] % 256),
                                    int(im.size[1] / 256)),
                        im.tobytes()))
        return buf