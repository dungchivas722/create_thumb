import os
from io import BytesIO
from rembg import remove
from PIL import Image
from streamlit_image_annotation import detection
import numpy as np
import streamlit as st
import streamlit_antd_components as sac
st.set_page_config(layout="wide", page_title="lamthumb", page_icon=":sunglasses:")
from streamlit_paste_button import paste_image_button as pbutton
from streamlit_text_label import label_select
from tienxuly.xulytext import draw_text
def load_profile():
    list_profile = []
    with open('nguyenlieu/profile.txt', 'r') as f:
        # phan tu cua list_type ung voi moi dong va gia tri ngan cach boi :
        for line in f:
            if line.strip() != "":
                list_profile.append(line.strip().split('|'))
    list_profile_show = [item[0] for item in list_profile]
    return list_profile,list_profile_show
if __name__ == "__main__":
    if 'list_profile_show' not in st.session_state:
        st.session_state['list_profile_show'] = ["dun"]
    if 'list_profile' not in st.session_state:
        st.session_state['list_profile'],st.session_state['list_profile_show'] = load_profile()
    st.title('Thumbnail :blue[v1.0] :sunglasses:')
    type = st.selectbox("Profile saved", st.session_state['list_profile_show'])
    load_file_config = st.button("Load file profile", use_container_width=True)
    if load_file_config:
        for key in st.session_state:
            del st.session_state[key]
        st.session_state['list_profile'],st.session_state['list_profile_show'] = load_profile()
        st.experimental_rerun()
    delete_profile = st.button("Delete profile", use_container_width=True)
    if delete_profile:
        # kiem tra xem neu chi co 1 phan tu thi khong xoa
        if len(st.session_state['list_profile']) == 1:
            st.error("Không thể xóa profile cuối cùng")
        else:
            st.session_state['list_profile'].pop(st.session_state['list_profile_show'].index(type))
            with open('nguyenlieu/profile.txt', 'w') as f:
                for item in st.session_state['list_profile']:
                    f.write(f'\n{item[0]}|{item[1]}')
            st.session_state['list_profile'],st.session_state['list_profile_show'] = load_profile()
            st.experimental_rerun()
    listprofile = st.session_state['list_profile'][st.session_state['list_profile_show'].index(type)]
    colpicture = st.columns([2, 5, 1])
    with colpicture[0]:
        img_np = None
        paste_result = pbutton("Paste an picture from clipbroard")
        upload_result = st.file_uploader("Upload an picture", type=["jpg", "jpeg", "png"])
        with st.expander("Check picture"):
            if paste_result.image_data is not None:
                st.write('Pasted image:')
                st.image(paste_result.image_data)
            elif upload_result is not None:
                st.write('Uploaded image:')
                st.image(upload_result)
        if paste_result.image_data is not None:
            img_np = np.array(paste_result.image_data)
        elif upload_result is not None:
            img_np = np.array(Image.open(upload_result))
        if img_np is not None:
            height, width, channels = img_np.shape
            image = Image.fromarray(img_np)
            st.write(f'Height: {height}, Width: {width}, Channels: {channels}')
            if channels == 4:
                image = image.convert("RGB")
            image.save('temp.jpg')
            with colpicture[1]:
                label_list = ['Crop']
                image_path_list = ['temp.jpg']
                if 'result_dict' not in st.session_state:
                    result_dict = {}
                    for img in image_path_list:
                        result_dict[img] = {'bboxes': [], 'labels': []}
                    st.session_state['result_dict'] = result_dict.copy()
                # target_image_path = temp_file_path
                target_image_path = image_path_list[0]
                new_labels = detection(image_path=target_image_path,
                                       bboxes=st.session_state['result_dict'][target_image_path]['bboxes'],
                                       labels=st.session_state['result_dict'][target_image_path]['labels'],
                                       label_list=label_list, key=target_image_path)
                # os.remove(temp_file_path)
                if new_labels is not None:
                    st.session_state['result_dict'][target_image_path]['bboxes'] = [v['bbox'] for v in new_labels]
                    st.session_state['result_dict'][target_image_path]['labels'] = [v['label_id'] for v in new_labels]
                chon_luon_anh = st.button("Choose full picture", use_container_width=True)
                if chon_luon_anh:
                    st.session_state['result_dict'][target_image_path]['bboxes'] = [[0, 0, width, height]]
            with colpicture[2]:
                if (len(st.session_state['result_dict'][target_image_path]['bboxes'])) != 1:
                    st.error("Just choose 1 box in picture")
                else:
                    st.write("Cropped image:")
                    bbox = st.session_state['result_dict'][target_image_path]['bboxes'][0]
                    left, top, width, height = bbox
                    right = left + width
                    bottom = top + height
                    cropped_image = image.crop((left, top, right, bottom))
                    st.image(cropped_image,use_column_width=True)
                    rembg_pic = sac.switch(label='Remove background', align='center', size='md',value=False)
                    if rembg_pic:
                        cropped_image = remove(cropped_image)
                        st.write("Background removed:")
                        st.image(cropped_image,use_column_width=True)

    #-------------
    with open('nguyenlieu/listcolor.txt', 'r') as f:
        list_color = f.read().split('\n')
    list_color_name = []
    list_color_code = []
    for item in list_color:
        if item.strip() == "":
            continue
        else:
            name, code = item.split("|")
            list_color_name.append(name.strip())
            list_color_code.append(code.strip())
    typeanh = 0
    font_path = "nguyenlieu/font"
    list_name_font = os.listdir(font_path)
    list_font = list_name_font
    #-------------
    coltitle = st.columns([3,1])
    with coltitle[0]:
        text_nhap_title = st.text_input("Type title",key="nhap title")
        selections_title = label_select(body=text_nhap_title, labels=list_color_name, interfaces=['controls', 'update'])
    with coltitle[1]:
        text_nhap_caunhanmanh = '-1'
        chon_nhan_manh = sac.switch(label='Choose strong text', align='center', size='md',value=False)
        if chon_nhan_manh:
            text_nhap_caunhanmanh = st.text_input("Type strong text",key="nhap cau nhan manh")
            if text_nhap_caunhanmanh != '':
                st.success("Type strong text success")
            else:
                st.error("Type strong text error")
                text_nhap_caunhanmanh = '-1'
    #---------------
    if len(listprofile) != 2:
        st.error("Profile error")
    else:
        name, link = listprofile
        link = link.split(',')
        indexvitrianh,indexvitritext,indexvitrinhanmanh,indexvitriviengiua,indexvitrivienngoai,mau_anh,mau_text,mau_nhanmanh,mau_viengiua,mau_vienngoai = link
        #---------------------------------
        indexvitrianh = int(indexvitrianh)
        indexvitritext = int(indexvitritext)
        indexvitrinhanmanh = int(indexvitrinhanmanh)
        indexvitriviengiua = bool(indexvitriviengiua)
        indexvitrivienngoai = bool(indexvitrivienngoai)
        # mau_anh ='-1'
        # mau_text = '#ff4466'
        # mau_nhanmanh = '-1'
        # mau_viengiua = '-1'
        # mau_vienngoai = '-1'

        #----------------------------------
        if 'option_text_trai' not in st.session_state:
            st.session_state['option_text_trai'] = True
        if 'option_text_phai' not in st.session_state:
            st.session_state['option_text_phai'] = True
        if 'option_vien_giua' not in st.session_state:
            st.session_state['option_vien_giua'] = False
        if 'option_vi_tri_nhan_manh_phia_text' not in st.session_state:
            st.session_state['option_vi_tri_nhan_manh_phia_text'] = True
        st.session_state['mau_anh'] = mau_anh
        st.session_state['mau_text'] = mau_text
        st.session_state['mau_nhanmanh'] = mau_nhanmanh
        st.session_state['mau_viengiua'] = mau_viengiua
        st.session_state['mau_vienngoai'] = mau_vienngoai
        #----------------------------------
        colthuoctinh = st.columns([2, 1, 2,1,1])
        with colthuoctinh[0]:
            vitrianh = sac.buttons([
                sac.ButtonsItem(label='Left'),
                sac.ButtonsItem(label='Right'),
                sac.ButtonsItem(label='Fullscreen'),
            ], label='Pic locate', align='center',return_index=True,index=indexvitrianh)
            if vitrianh == 0:
                st.session_state['option_text_trai'] = True
                st.session_state['option_text_phai'] = False
                st.session_state['option_vien_giua'] = False
                st.session_state['option_vi_tri_nhan_manh_phia_text'] = False
                if st.session_state['mau_anh'] == '-1':
                    st.session_state['mau_anh'] = "#ffffff"
                st.session_state['mau_anh'] = st.color_picker('Choose screen background color',st.session_state['mau_anh'])
                indexvitritext = 1
            elif vitrianh == 1:
                st.session_state['option_text_trai'] = False
                st.session_state['option_text_phai'] = True
                st.session_state['option_vien_giua'] = False
                st.session_state['option_vi_tri_nhan_manh_phia_text'] = False
                if st.session_state['mau_anh'] == '-1':
                    st.session_state['mau_anh'] = "#ffffff"
                st.session_state['mau_anh'] = st.color_picker('Choose screen background color',st.session_state['mau_anh'])
                indexvitritext = 0
            else:
                st.session_state['option_text_trai'] = False
                st.session_state['option_text_phai'] = False
                st.session_state['option_vien_giua'] = True
                st.session_state['option_vi_tri_nhan_manh_phia_text'] = True
                st.session_state['mau_anh'] = '-1'
                indexvitritext = 0
                indexvitrinhanmanh = 1

        with colthuoctinh[1]:
            vitritext = sac.buttons([
                sac.ButtonsItem(label='Left',disabled=st.session_state['option_text_trai']),
                sac.ButtonsItem(label='Right',disabled=st.session_state['option_text_phai']),
            ], label='Text locate', align='center',return_index=True,index=indexvitritext)
            st.session_state['mau_text'] = st.color_picker('Choose text background color',st.session_state['mau_text'])
        with colthuoctinh[2]:
            vitricaunhanmanh = sac.buttons([
                sac.ButtonsItem(label='Text side',disabled= st.session_state['option_vi_tri_nhan_manh_phia_text']),
                sac.ButtonsItem(label='All side',disabled=False),
                sac.ButtonsItem(label='No side',disabled=False),
            ], label='Strong text locate', align='center',return_index=True,index=indexvitrinhanmanh)
            if vitricaunhanmanh == 2:
                st.session_state['mau_nhanmanh'] = '-1'
            else:
                if  st.session_state['mau_nhanmanh'] == '-1':
                    st.session_state['mau_nhanmanh'] = "#ffffff"
                st.session_state['mau_nhanmanh'] = st.color_picker( 'Choose strong text background color',st.session_state['mau_nhanmanh'])
        with colthuoctinh[3]:
            vitriviengiua = sac.switch(label='Middle border', align='center', size='md',disabled=st.session_state['option_vien_giua'],value=indexvitriviengiua)
            if not st.session_state['option_vien_giua'] and vitriviengiua:
                if st.session_state['mau_viengiua'] == '-1':
                    st.session_state['mau_viengiua'] = "#ffffff"
                st.session_state['mau_viengiua'] = st.color_picker('Choose middle border background color',st.session_state['mau_viengiua'])
            else:
                st.session_state['mau_viengiua'] = '-1'
        with colthuoctinh[4]:
            vitrivienngoai = sac.switch(label='Outline', align='center', size='md',disabled=False,value=indexvitrivienngoai)
            if vitrivienngoai:
                if st.session_state['mau_vienngoai'] == '-1':
                    st.session_state['mau_vienngoai'] = "#ffffff"
                st.session_state['mau_vienngoai'] = st.color_picker('Choose outline background color',st.session_state['mau_vienngoai'])
            else:
                st.session_state['mau_vienngoai'] = '-1'

        #---------------------------------------------------------------------------------------------------------------------------
        colsaveprofile = st.columns([1, 1, 1,1])
        if "name_profile" not in st.session_state:
            st.session_state["name_profile"] = ""
        ten_hop_le = True
        with colsaveprofile[0]:
            # save vao file config
            name_profile = st.text_input("Type name profile",value=st.session_state["name_profile"])
            for item in st.session_state['list_profile']:
                item_check = item[0].strip().lower()
                if name_profile.strip().lower() == item_check:
                    with colsaveprofile[1]:
                        st.error("Name profile already exists")
                        ten_hop_le = False
                        break
                elif name_profile.strip().lower() == "":
                    with colsaveprofile[1]:
                        ten_hop_le = False
                        st.error("Name profile is empty")
                        break
            if ten_hop_le:
                with colsaveprofile[1]:
                    st.success("Name profile is valid")
                with colsaveprofile[2]:
                    if st.button("Save profile", key=f"save_{name_profile}",use_container_width=True):
                        with open('nguyenlieu/profile.txt', 'a') as f:
                            f.write(f'\n{name_profile}|{vitrianh},{vitritext},{vitricaunhanmanh},{vitriviengiua},{vitrivienngoai},{st.session_state["mau_anh"]},{st.session_state["mau_text"]},{st.session_state["mau_nhanmanh"]},{st.session_state["mau_viengiua"]},{st.session_state["mau_vienngoai"]}')
                        st.session_state['name_profile'] = ""
                        st.session_state['list_profile'],st.session_state['list_profile_show'] = load_profile()
                        for key in st.session_state:
                            del st.session_state[key]
                        st.experimental_rerun()
    #-------------------------------------------------------------------------------------------------------------------
    if vitrianh==0 and vitritext==1 and vitricaunhanmanh == 0:
        typeanh = 1
    elif vitrianh==0 and vitritext==1 and vitricaunhanmanh == 1:
        typeanh = 2
    elif vitrianh==0 and vitritext==1 and vitricaunhanmanh == 2:
        typeanh = 3
    elif vitrianh==1 and vitritext==0 and vitricaunhanmanh == 0:
        typeanh = 4
    elif vitrianh==1 and vitritext==0 and vitricaunhanmanh == 1:
        typeanh = 5
    elif vitrianh==1 and vitritext==0 and vitricaunhanmanh == 2:
        typeanh = 6
    elif vitrianh==2 and vitritext==0 and vitricaunhanmanh == 1:
        typeanh = 7
    elif vitrianh==2 and vitritext==0 and vitricaunhanmanh == 2:
        typeanh = 8
    elif vitrianh==2 and vitritext==1 and vitricaunhanmanh == 1:
        typeanh = 9
    elif vitrianh==2 and vitritext==1 and vitricaunhanmanh == 2:
        typeanh = 10
    colrenanh = st.columns([4, 4])
    with colrenanh[1]:
        colthuoctinhfont = st.columns([1, 1, 1, 1, 1])
        with colthuoctinhfont[0]:
            font_chu = st.selectbox("Font text", list_font)
            font_chu_nhanmanh = st.selectbox("Font strong text", list_font)
        with colthuoctinhfont[1]:
            kichthuoc_font = st.number_input("Font size",min_value=20,max_value=1000,value=100,step=20)
            kichthuoc_font_nhanmanh = st.number_input("Strong font size",min_value=20,max_value=1000,value=100,step=20)
        with colthuoctinhfont[2]:
            khoachcach_chu = st.number_input("Space between text",min_value=0,max_value=1000,value=0,step=10)
            khoachcach_chu_nhanmanh = st.number_input("Space between strong text",min_value=0,max_value=1000,value=0,step=10)
        with colthuoctinhfont[3]:
            mau_chu = st.color_picker("Text color","#ffffff")
            mau_chu_nhanmanh = st.color_picker("Strong text color","#ffffff")
        with colthuoctinhfont[4]:
            can_le_chu = st.selectbox("Text align",["left","center","right"])
            can_le_chu_nhanmanh = st.selectbox("Strong text align",["left","center","right"])
        with colthuoctinhfont[0]:
            gach_doc = st.number_input("Strikethrough RtoL", min_value=10, max_value=1920, value=600,step=50)
        with colthuoctinhfont[1]:
            gach_ngang = st.number_input("Underlined UPtoDown", min_value=10, max_value=1080, value=600,step=50)
        with colthuoctinhfont[2]:
            do_day_vien_giua = st.number_input("Middle border thickness", min_value=1, max_value=40, value=2)
        with colthuoctinhfont[3]:
            do_day_vien_ngoai = st.number_input("Outline thickness", min_value=1, max_value=40, value=2)
        with colthuoctinhfont[4]:
            start_text = st.number_input("Start text", min_value=0, max_value=1920, value=0,step=10)
        st.divider()
        colfullscreen = st.columns([1, 1,1,1])
        with colfullscreen[0]:
            width_full_name = st.number_input("Width of title for fullscreen", min_value=10, max_value=1920, value=600,step=50)
        with colfullscreen[1]:
            height_full_name = st.number_input("Height of title for fullscreen", min_value=10, max_value=1080, value=600,step=50)
        with colfullscreen[2]:
            x_fullscreen = st.number_input("Start x of title for fullscreen", min_value=0, max_value=1920, value=0,step=10)
        with colfullscreen[3]:
            y_fullscreen = st.number_input("Start y of title for fullscreen", min_value=0, max_value=1080, value=0,step=10)
        back_title_fullscreen = sac.switch(label='Background title for fullscreen', align='center', size='md',value=False)
    if st.session_state['mau_anh'] == '-1':
        st.session_state['mau_anh'] = "#ffffff"
    img_thumb = Image.new('RGBA', (1920, 1080), color=st.session_state['mau_anh'])
    with colrenanh[0]:
        if typeanh == 0 :
            st.error("No type")
        elif text_nhap_title == "":
            st.error("No Type title")
        else:
            if typeanh== 1:
                # anh trai , text phai, nhan manh phia text
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((1920-gach_doc, 1080)))
                    img_thumb.paste(img_anh, (0, 0))
                else:
                    img_anh = -1
                # tao text
                img_text = Image.new('RGB', (gach_doc, gach_ngang), color = st.session_state['mau_text'])
                img_thumb.paste(img_text, (1920-gach_doc, 0))
                # tao nhan manh
                img_nhan_manh_text = Image.new('RGB', (gach_doc,1080 - gach_ngang), color = st.session_state['mau_nhanmanh'])
                img_thumb.paste(img_nhan_manh_text, (1920-gach_doc, gach_ngang))
                if vitriviengiua:
                    img_viengiua1 = Image.new('RGB', (do_day_vien_giua*4, 1080), color = st.session_state['mau_viengiua'])
                    img_viengiua2 = Image.new('RGB', (gach_doc, do_day_vien_giua*4), color = st.session_state['mau_viengiua'])
                    img_thumb.paste(img_viengiua1, (1920-gach_doc-do_day_vien_giua*2, 0))
                    img_thumb.paste(img_viengiua2, (1920-gach_doc, gach_ngang-do_day_vien_giua*2))
                if vitrivienngoai:
                    img_vienngoaidai = Image.new('RGB', (do_day_vien_ngoai * 4, 1080),color=st.session_state['mau_vienngoai'])
                    img_viengiuarong = Image.new('RGB', (1920,do_day_vien_ngoai * 4),color=st.session_state['mau_vienngoai'])
                    img_thumb.paste(img_vienngoaidai, (0, 0))
                    img_thumb.paste(img_vienngoaidai, (1920-do_day_vien_ngoai*4, 0))
                    img_thumb.paste(img_viengiuarong, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 1080-do_day_vien_ngoai*4))
                if vitriviengiua and vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_giua*2 - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc + do_day_vien_giua*2 , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = gach_doc - do_day_vien_giua * 2 - do_day_vien_ngoai * 4, 1080 - gach_ngang - do_day_vien_ngoai * 4 - do_day_vien_giua * 2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (1920 - gach_doc + do_day_vien_giua * 2, gach_ngang + do_day_vien_giua * 2),
                                        mask=img_text_caunhanmanh.split()[3])
                elif vitriviengiua and not vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_giua*2  ,gach_ngang - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc + do_day_vien_giua*2 , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = gach_doc - do_day_vien_giua * 2, 1080 - gach_ngang - do_day_vien_giua * 2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (1920 - gach_doc + do_day_vien_giua * 2, gach_ngang + do_day_vien_giua * 2),mask=img_text_caunhanmanh.split()[3])
                elif not vitriviengiua and vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc , 0+do_day_vien_ngoai*4),mask=img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = gach_doc - do_day_vien_ngoai * 4, 1080 - gach_ngang - do_day_vien_ngoai * 4
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (1920 - gach_doc, gach_ngang + do_day_vien_ngoai * 4),mask=img_text_caunhanmanh.split()[3])
                else:
                    width_title,height_title = gach_doc ,gach_ngang
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc , 0))
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = gach_doc, 1080 - gach_ngang
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (1920 - gach_doc, gach_ngang),mask=img_text_caunhanmanh.split()[3])
            if typeanh==3:
                # anh trai , text phai, khong nhan manh
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((1920-gach_doc, 1080)))
                    img_thumb.paste(img_anh, (0, 0))
                else:
                    img_anh = -1
                # tao text
                img_text = Image.new('RGB', (gach_doc, 1080), color = st.session_state['mau_text'])
                img_thumb.paste(img_text, (1920-gach_doc, 0))
                if vitriviengiua:
                    img_viengiua1 = Image.new('RGB', (do_day_vien_giua*4, 1080), color = st.session_state['mau_viengiua'])
                    img_thumb.paste(img_viengiua1, (1920-gach_doc-do_day_vien_giua*2, 0))
                if vitrivienngoai:
                    img_vienngoaidai = Image.new('RGB', (do_day_vien_ngoai * 4, 1080),color=st.session_state['mau_vienngoai'])
                    img_viengiuarong = Image.new('RGB', (1920,do_day_vien_ngoai * 4),color=st.session_state['mau_vienngoai'])
                    img_thumb.paste(img_vienngoaidai, (0, 0))
                    img_thumb.paste(img_vienngoaidai, (1920-do_day_vien_ngoai*4, 0))
                    img_thumb.paste(img_viengiuarong, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 1080-do_day_vien_ngoai*4))
                if vitriviengiua and vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_giua*4 - do_day_vien_ngoai*4 ,1080 - do_day_vien_ngoai*8
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc + do_day_vien_giua*4 , do_day_vien_ngoai*4),mask=img_text_title.split()[3])
                elif vitriviengiua and not vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_giua*4 ,1080
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc + do_day_vien_giua*4 , 0),mask=img_text_title.split()[3])
                elif not vitriviengiua and vitrivienngoai:
                    width_title,height_title = gach_doc + do_day_vien_giua*4 ,1080 - do_day_vien_ngoai*8
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc , 0+do_day_vien_ngoai*4),mask=img_text_title.split()[3])
                elif not vitriviengiua and not vitrivienngoai:
                    width_title,height_title = gach_doc ,1080
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920-gach_doc , 0),mask=img_text_title.split()[3])
                else:
                    st.error("No type")
            if typeanh==2:
                # anh trai , text phai, nhan manh all
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((1920-gach_doc, gach_ngang)))
                    img_thumb.paste(img_anh, (0, 0))
                else:
                    img_anh = -1
                # tao text
                img_text = Image.new('RGB', (gach_doc, gach_ngang), color = st.session_state['mau_text'])
                img_thumb.paste(img_text, (1920-gach_doc, 0))
                # tao nhan manh
                img_nhan_manh_text = Image.new('RGB', (1920,1080 - gach_ngang), color = st.session_state['mau_nhanmanh'])
                img_thumb.paste(img_nhan_manh_text, (0, gach_ngang))
                if vitriviengiua:
                    img_viengiua1 = Image.new('RGB', (do_day_vien_giua*4, gach_ngang), color = st.session_state['mau_viengiua'])
                    img_viengiua2 = Image.new('RGB', (1920, do_day_vien_giua*4), color = st.session_state['mau_viengiua'])
                    img_thumb.paste(img_viengiua1, (1920-gach_doc-do_day_vien_giua*2, 0))
                    img_thumb.paste(img_viengiua2, (0, gach_ngang-do_day_vien_giua*2))
                if vitrivienngoai:
                    img_vienngoaidai = Image.new('RGB', (do_day_vien_ngoai * 4, 1080),color=st.session_state['mau_vienngoai'])
                    img_viengiuarong = Image.new('RGB', (1920,do_day_vien_ngoai * 4),color=st.session_state['mau_vienngoai'])
                    img_thumb.paste(img_vienngoaidai, (0, 0))
                    img_thumb.paste(img_vienngoaidai, (1920-do_day_vien_ngoai*4, 0))
                    img_thumb.paste(img_viengiuarong, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 1080-do_day_vien_ngoai*4))
                if vitriviengiua and vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_ngoai*4 - do_day_vien_giua*2  ,gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920 -gach_doc+do_day_vien_giua*2 , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 - do_day_vien_ngoai*8, 1080 - gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0+do_day_vien_ngoai*4, gach_ngang+do_day_vien_giua*2), mask = img_text_caunhanmanh.split()[3])
                elif vitriviengiua and not vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_giua*2  ,gach_ngang - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920 -gach_doc+do_day_vien_giua*2 , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 - do_day_vien_giua*4, 1080 - gach_ngang - do_day_vien_giua*2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0+do_day_vien_ngoai*4, gach_ngang+do_day_vien_giua*2), mask = img_text_caunhanmanh.split()[3])
                elif not vitriviengiua and vitrivienngoai:
                    width_title,height_title = gach_doc - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920 -gach_doc , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 - do_day_vien_ngoai*8, 1080 - gach_ngang - do_day_vien_ngoai*4
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0+do_day_vien_ngoai*4, gach_ngang), mask = img_text_caunhanmanh.split()[3])
                else:
                    width_title,height_title = gach_doc ,gach_ngang
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (1920 -gach_doc , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 ,gach_ngang
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0, gach_ngang), mask = img_text_caunhanmanh.split()[3])
            if typeanh==4:
                # anh phai , text trai, nhan manh phia text
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((gach_doc, 1080)))
                    img_thumb.paste(img_anh, (1920-gach_doc, 0))
                else:
                    img_anh = -1
                # tao text
                img_text = Image.new('RGB', (1920-gach_doc, gach_ngang), color = st.session_state['mau_text'])
                img_thumb.paste(img_text, (0, 0))
                # tao nhan manh
                img_nhan_manh_text = Image.new('RGB', (1920-gach_doc,1080 - gach_ngang), color = st.session_state['mau_nhanmanh'])
                img_thumb.paste(img_nhan_manh_text, (0, gach_ngang))
                if vitriviengiua:
                    img_viengiua1 = Image.new('RGB', (do_day_vien_giua*4, 1080), color = st.session_state['mau_viengiua'])
                    img_viengiua2 = Image.new('RGB', (1920-gach_doc, do_day_vien_giua*4), color = st.session_state['mau_viengiua'])
                    img_thumb.paste(img_viengiua1, (1920 - gach_doc-do_day_vien_giua*2, 0))
                    img_thumb.paste(img_viengiua2, (0, gach_ngang-do_day_vien_giua*2))
                if vitrivienngoai:
                    img_vienngoaidai = Image.new('RGB', (do_day_vien_ngoai * 4, 1080),color=st.session_state['mau_vienngoai'])
                    img_viengiuarong = Image.new('RGB', (1920,do_day_vien_ngoai * 4),color=st.session_state['mau_vienngoai'])
                    img_thumb.paste(img_vienngoaidai, (0, 0))
                    img_thumb.paste(img_vienngoaidai, (1920-do_day_vien_ngoai*4, 0))
                    img_thumb.paste(img_viengiuarong, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 1080-do_day_vien_ngoai*4))
                if vitriviengiua and vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_giua*2 - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0+do_day_vien_ngoai*4 , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920-gach_doc - do_day_vien_giua*2 - do_day_vien_ngoai*4, 1080 - gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0+do_day_vien_ngoai*4, gach_ngang + do_day_vien_giua*2), mask = img_text_caunhanmanh.split()[3])
                elif vitriviengiua and not vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_giua*2  ,gach_ngang - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0 , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920-gach_doc - do_day_vien_giua*2, 1080 - gach_ngang - do_day_vien_giua*2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0 , gach_ngang + do_day_vien_giua*2), mask = img_text_caunhanmanh.split()[3])
                elif not vitriviengiua and vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (do_day_vien_ngoai*4 , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920-gach_doc - do_day_vien_ngoai*4, 1080 - gach_ngang - do_day_vien_ngoai*4
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        ( do_day_vien_ngoai*4, gach_ngang), mask = img_text_caunhanmanh.split()[3])
                else:
                    width_title,height_title = 1920-gach_doc ,gach_ngang
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0 , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920-gach_doc ,gach_ngang
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0 , gach_ngang), mask = img_text_caunhanmanh.split()[3])
            if typeanh==6:
             # anh phai , text trai, khong nhan manh
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((gach_doc, 1080)))
                    img_thumb.paste(img_anh, (1920-gach_doc, 0))
                else:
                    img_anh = -1
                # tao text
                img_text = Image.new('RGB', (1920-gach_doc, 1080), color = st.session_state['mau_text'])
                img_thumb.paste(img_text, (0, 0))
                if vitriviengiua:
                    img_viengiua1 = Image.new('RGB', (do_day_vien_giua*4, 1080), color = st.session_state['mau_viengiua'])
                    img_thumb.paste(img_viengiua1, (1920-gach_doc-do_day_vien_giua*2, 0))
                if vitrivienngoai:
                    img_vienngoaidai = Image.new('RGB', (do_day_vien_ngoai * 4, 1080),color=st.session_state['mau_vienngoai'])
                    img_viengiuarong = Image.new('RGB', (1920,do_day_vien_ngoai * 4),color=st.session_state['mau_vienngoai'])
                    img_thumb.paste(img_vienngoaidai, (1920-do_day_vien_ngoai*4, 0))
                    img_thumb.paste(img_vienngoaidai, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 1080-do_day_vien_ngoai*4))
                if vitriviengiua and vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_giua*2 - do_day_vien_ngoai*4 ,1080 - do_day_vien_ngoai*8
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0+do_day_vien_ngoai*4 , do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                elif vitriviengiua and not vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_giua*2 ,1080
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0 , 0), mask = img_text_title.split()[3])
                elif not vitriviengiua and vitrivienngoai:
                    width_title,height_title = 1920-gach_doc ,1080 - do_day_vien_ngoai*8
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0+do_day_vien_ngoai*4, 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                else:
                    width_title,height_title = 1920-gach_doc ,1080
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0 , 0), mask = img_text_title.split()[3])
            if typeanh==5:
               # anh phai , text trai, nhan manh all
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((gach_doc, gach_ngang)))
                    img_thumb.paste(img_anh, (1920-gach_doc, 0))
                else:
                    img_anh = -1
                # tao text
                img_text = Image.new('RGB', (1920-gach_doc, gach_ngang), color = st.session_state['mau_text'])
                img_thumb.paste(img_text, (0, 0))
                # tao nhan manh
                img_nhan_manh_text = Image.new('RGB', (1920,1080 - gach_ngang), color = st.session_state['mau_nhanmanh'])
                img_thumb.paste(img_nhan_manh_text, (0, gach_ngang))
                if vitriviengiua:
                    img_viengiua1 = Image.new('RGB', (do_day_vien_giua*4, gach_ngang), color = st.session_state['mau_viengiua'])
                    img_viengiua2 = Image.new('RGB', (1920, do_day_vien_giua*4), color = st.session_state['mau_viengiua'])
                    img_thumb.paste(img_viengiua1, (1920-gach_doc-do_day_vien_giua*2, 0))
                    img_thumb.paste(img_viengiua2, (0, gach_ngang-do_day_vien_giua*2))
                if vitrivienngoai:
                    img_vienngoaidai = Image.new('RGB', (do_day_vien_ngoai * 4, 1080),color=st.session_state['mau_vienngoai'])
                    img_viengiuarong = Image.new('RGB', (1920,do_day_vien_ngoai * 4),color=st.session_state['mau_vienngoai'])
                    img_thumb.paste(img_vienngoaidai, (0, 0))
                    img_thumb.paste(img_vienngoaidai, (1920-do_day_vien_ngoai*4, 0))
                    img_thumb.paste(img_viengiuarong, (0, 0))
                    img_thumb.paste(img_viengiuarong, (0, 1080-do_day_vien_ngoai*4))
                if vitriviengiua and vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_giua*2 - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0+do_day_vien_ngoai*4 , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 - do_day_vien_ngoai*8, 1080 - gach_ngang - do_day_vien_ngoai*4 - do_day_vien_giua*2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0+do_day_vien_ngoai*4, gach_ngang + do_day_vien_giua*2), mask = img_text_caunhanmanh.split()[3])
                elif vitriviengiua and not vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_giua*2  ,gach_ngang - do_day_vien_giua*2
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0 , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920, 1080 - gach_ngang - do_day_vien_giua*2
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0, gach_ngang+do_day_vien_giua*2), mask = img_text_caunhanmanh.split()[3])
                elif not vitriviengiua and vitrivienngoai:
                    width_title,height_title = 1920-gach_doc - do_day_vien_ngoai*4  ,gach_ngang - do_day_vien_ngoai*4
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (do_day_vien_ngoai*4 , 0+do_day_vien_ngoai*4), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 - do_day_vien_ngoai*8, 1080 - gach_ngang - do_day_vien_ngoai*4
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0+do_day_vien_ngoai*4, gach_ngang), mask = img_text_caunhanmanh.split()[3])
                else:
                    width_title,height_title = 1920-gach_doc ,gach_ngang
                    img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_title,height_title,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                    img_thumb.paste(img_text_title, (0 , 0), mask = img_text_title.split()[3])
                    if chon_nhan_manh and text_nhap_caunhanmanh != '-1':
                        selections_caunhamanh = [
                            f"Selection(start=0, end={len(text_nhap_caunhanmanh)}, text='{text_nhap_caunhanmanh}', labels=['{mau_chu_nhanmanh}'])"]
                        width_caunhanmanh, height_caunhanmanh = 1920 ,gach_ngang
                        img_text_caunhanmanh = draw_text(selections_caunhamanh, text_nhap_caunhanmanh, mau_chu_nhanmanh,
                                                         width_caunhanmanh, height_caunhanmanh, kichthuoc_font_nhanmanh,
                                                         font_chu_nhanmanh, can_le_chu_nhanmanh,
                                                         khoachcach_chu_nhanmanh,start_text)
                        img_thumb.paste(img_text_caunhanmanh,
                                        (0, gach_ngang), mask = img_text_caunhanmanh.split()[3])
            if typeanh==7 or typeanh==8 or typeanh==9 or typeanh==10:
                # anh full man hinh, text trai, khong nhan manh
                # tao anh
                if paste_result.image_data is not None and (len(st.session_state['result_dict'][target_image_path]['bboxes'])) == 1:
                    img_anh = (cropped_image.resize((1920, 1080)))
                    img_thumb.paste(img_anh, (0, 0))
                else:
                    img_anh = -1

                # tao text
                img_text_title = draw_text(selections_title,text_nhap_title,mau_chu,width_full_name,height_full_name,kichthuoc_font,font_chu,can_le_chu,khoachcach_chu,start_text)
                if back_title_fullscreen:
                    img_thumb.paste(img_text_title, (x_fullscreen, y_fullscreen))
                else:
                    img_thumb.paste(img_text_title, (x_fullscreen, y_fullscreen), mask=img_text_title.split()[3])
            st.image(img_thumb)

    colsavepic = st.columns([1,1,1,1,1,1])
    with colsavepic[0]:
        duong_dan_thumuc = st.text_input("Folder path to save picture", value = "C:/Users/dun/Desktop")
        with colsavepic[1]:
            st.code(duong_dan_thumuc)
        with colsavepic[2]:
            if st.button("Save picture"):
                if not os.path.exists(duong_dan_thumuc):
                    os.makedirs(duong_dan_thumuc)
                img_thumb.save(duong_dan_thumuc + "/thumbnail_clone_dun.png")
                with colsavepic[4]:
                    if os.path.exists(duong_dan_thumuc + "/thumbnail_clone_dun.png"):
                        st.success("Save picture successfully")
                    else:
                        st.error("Error saving picture")
    with colsavepic[3]:
        buffer = BytesIO()
        img_thumb.save(buffer, format="PNG")
        buffer.seek(0)
        st.download_button(label="Download picture",data=buffer,file_name="thumbnail_clone_dun.png",mime="image/png")


















