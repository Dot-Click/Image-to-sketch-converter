import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision import models
import matplotlib.pyplot as plt

# Load the pre-trained model using the new 'weights' argument
weights = models.segmentation.DeepLabV3_ResNet101_Weights.DEFAULT
model = models.segmentation.deeplabv3_resnet101(weights=weights)
model.eval()

# Manually specify the normalization values
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load and preprocess the image
image = Image.open('D:/python/image_outline/input/img2.jpeg')
input_tensor = transform(image).unsqueeze(0)

# Perform inference
with torch.no_grad():
    output = model(input_tensor)['out'][0]
output_predictions = output.argmax(0).cpu().numpy()

# Display the result
plt.imshow(output_predictions, cmap='gray')
plt.axis('off')
plt.savefig('D:/python/image_outline/outputs/model6/monoline_image.png')
