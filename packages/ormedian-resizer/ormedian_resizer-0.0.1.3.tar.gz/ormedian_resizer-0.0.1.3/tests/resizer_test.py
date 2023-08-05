from src.ormedian_resizer.resize_imgs import resizer
# folder_path = '/home/iamshri/Desktop/tests'
folder_path = '../tests/testImages'


resizer((100, 100), folder_path,  'resizedImages', 100, n_f=True, view=True, out_format='jpg')
