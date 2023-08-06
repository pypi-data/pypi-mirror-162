from PIL import Image, ImageDraw, ImageFont
from .machine import StateMachine, StateMachineIo
from .test import gen_states, test_machine
import math

def gen_graph(machine : StateMachine, i : StateMachineIo, s : StateMachineIo, font)->Image:
    res = test_machine(machine, i, s)
    state_count = len(res.states)
    angle = 6.28/state_count
    size = state_count*128
    img = Image.new('RGB', (int(1.618*size), size), color='white')
    draw = ImageDraw.Draw(img)

    _font = ImageFont.truetype(font, 16)

    r = 32
    for i in range(state_count):
        pos_x = math.sin(i*angle)*size/3+size/2
        pos_y = math.cos(i*angle)*size/3+size/2
        draw.ellipse([pos_x-r,pos_y-r,pos_x+r,pos_y+r],outline='black')
        text = ','.join([str(k) for k in list(res.states[i])])
        bbox = draw.textbbox([pos_x, pos_y], text, font=_font)
        draw.text([bbox[0]-(bbox[2]-bbox[0])/2,bbox[1]-(bbox[3]-bbox[1])/2], text, font=_font, fill='black')
    
    lines = {}
    for i in range(len(res.data)):
        s1 = res.data[i][0]
        s2 = res.data[i][2]
        info = ','.join([str(k) for k in res.data[i][1]])+'/'+','.join([str(k) for k in res.data[i][3]])
        if not (s1,s2) in lines.keys():
            lines[(s1,s2)] = [info]
        else:
            lines[(s1,s2)].append(info)

    for k, v in lines.items():
        s1 = k[0]
        s2 = k[1]
        pos1_x = math.sin(s1*angle)*size/3+size/2
        pos1_y = math.cos(s1*angle)*size/3+size/2
        pos2_x = math.sin(s2*angle)*size/3+size/2
        pos2_y = math.cos(s2*angle)*size/3+size/2
        dx = pos2_x - pos1_x
        dy = pos2_y - pos1_y
        dl = math.sqrt(dx*dx+dy*dy)
        if s1!=s2:
            ix = dx/dl
            iy = dy/dl
            lx = -iy
            ly = ix
            draw.line([pos1_x+ix*r,pos1_y+iy*r,pos2_x-ix*r,pos2_y-iy*r],fill='black')
            draw.line([pos2_x-ix*r,pos2_y-iy*r,pos2_x-ix*(r+4)+lx*3,pos2_y-iy*(r+4)+ly*3],fill='black')
            draw.line([pos2_x-ix*r,pos2_y-iy*r,pos2_x-ix*(r+4)-lx*3,pos2_y-iy*(r+4)-ly*3],fill='black')
            tx = pos1_x+ix*72
            ty = pos1_y+iy*72
        else:
            draw.ellipse([pos1_x-r/2+r*math.sin(s1*angle),pos1_y-r/2+r*math.cos(s1*angle),pos1_x+r/2+r*math.sin(s1*angle),pos1_y+r/2+r*math.cos(s1*angle)], outline='black')  
            tx = pos1_x+2*r*math.sin(s1*angle)
            ty = pos1_y+2*r*math.cos(s1*angle)
        draw.multiline_text([tx,ty], '\n'.join(v),fill='black',font=_font)


    draw.text([0,0], 'state: '+','.join(res.k2)+'\tinput: '+','.join(res.k1)+'\toutput: '+','.join(res.k3),font=_font,fill='red')
    return img
