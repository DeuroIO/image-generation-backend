import os

models = ['style_cezanne_cpu_pretrained', 'style_monet_cpu_pretrained', 'style_ukiyoe_cpu_pretrained', 'style_vangogh_cpu_pretrained']

def process_a_image_using_gan(prefix):
    for model in models:
        print(model)
        # 15 seconds to finish on the server
        COMMAND = "cd CycleGAN && DATA_ROOT=../s3_files/{} name={} model=one_direction_test phase=test loadSize=700 fineSize=700 gpu=0 cudnn=0 resize_or_crop=\"scale_width\" th test.lua && cd ..".format(prefix, model)
        print(COMMAND)
        os.system(COMMAND)
