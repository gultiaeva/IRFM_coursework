from app.application import app
import os

data_dir = 'app/static/data'
images_dir = 'app/static/images'
pdf_dir = os.path.join(data_dir, 'pdf')
txt_dir = os.path.join(data_dir, 'txt')
norm_dir = os.path.join(data_dir, 'norm')

for directory in [data_dir, images_dir, pdf_dir, txt_dir, norm_dir]:
    if not os.path.exists(directory):
        os.mkdir(directory)
