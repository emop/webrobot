'''
Created on 2013-7-5

@author: deonwu
'''

from Captcha import get_captcha


def create_captcha_image(input_path, out_path, box):
    from PIL import Image
    
    # size is width/height
    img = Image.open(input_path)
    #box = (2407, 804, 71, 796)
    area = img.crop(box)    
    area.save(out_path, 'png')
    #img.close()
    pass