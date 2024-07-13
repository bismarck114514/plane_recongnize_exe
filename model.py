import torch
from torchvision import transforms
from PIL import Image
import os
import torchvision.models as models

def build_model(num_classes):
    model = models.vgg16(weights=models.VGG16_Weights.DEFAULT)
    model.classifier[6] = torch.nn.Linear(4096, num_classes)
    return model

class AirplaneClassifier:
    def __init__(self, model_path, num_classes, device):
        self.model_path = model_path
        self.device = device
        self.num_classes = num_classes
        self.model = self.load_model()
        self.preprocess = transforms.Compose([
            transforms.Lambda(lambda img: img.convert('RGB') if img.mode == 'RGBA' else img),
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.class_names = ["直升机", "战斗机", "民航客机"]

    def load_model(self):
        model = build_model(self.num_classes)
        model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        model = model.to(self.device)
        model.eval()
        return model

    def predict_image(self, image_path):
        image = Image.open(image_path)
        image = self.preprocess(image)
        image = image.unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(image)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            _, preds = torch.max(outputs, 1)
        return preds.item(), probabilities
