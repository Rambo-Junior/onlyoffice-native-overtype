#!/usr/bin/env python3
"""Regenerate independently drawn OVR icons using Pillow; no third-party art."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
fonts=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
fontfile=next((x for x in fonts if Path(x).is_file()),None)
for px,name in [(48,'icon.png'),(96,'icon@2x.png')]:
    ss=px*4
    im=Image.new('RGBA',(ss,ss),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((3*ss//100,3*ss//100,97*ss//100,97*ss//100),radius=18*ss//100,fill=(41,55,84,255))
    d.rectangle((18*ss//100,23*ss//100,23*ss//100,77*ss//100),fill=(117,224,205,255))
    d.rounded_rectangle((33*ss//100,25*ss//100,83*ss//100,75*ss//100),radius=8*ss//100,outline=(251,252,255,255),width=3*ss//100)
    if fontfile:
        font=ImageFont.truetype(fontfile,25*ss//100)
        d.text((58*ss//100,50*ss//100),'OVR',font=font,anchor='mm',fill=(251,252,255,255),stroke_width=0)
    im.resize((px,px),Image.Resampling.LANCZOS).save(root/'plugin/resources'/name,optimize=True)
