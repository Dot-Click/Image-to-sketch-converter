from image_models.model2 import model2
from image_models.model3 import model3
from image_models.model4 import model4
from image_models.model5 import model5 

input_image_path = 'D:/python/image_outline/input/img2.jpeg'
output_image_path = 'D:/python/image_outline/outputs/model3/img2.jpeg'
modelname = 'model3' #2 to 5

if modelname == 'model2':
    model2(input_image_path,output_image_path)
elif modelname == 'model3':
    model3(input_image_path,output_image_path)
    
elif modelname == 'model4':
    model4(input_image_path,output_image_path)
    
elif modelname == 'model5':
    model5(input_image_path,output_image_path)
    