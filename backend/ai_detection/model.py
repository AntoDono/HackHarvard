import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models import resnet50, ResNet50_Weights
from torchvision import transforms
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from copy import deepcopy
from PIL import Image
from tqdm import tqdm
import torch.nn.functional as F


class DeepfakeDataset(Dataset):
    """Custom dataset class for deepfake detection"""
    
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        img_path, label = self.data[idx, 0], self.data[idx, 1]
        
        img = Image.open(img_path).convert("RGB")
        img = np.array(img)
        
        if self.transform:
            img = self.transform(img)
        
        # Convert label to int64 (Long tensor)
        return img, int(label)


class ResNetDeepfakeDetector(nn.Module):
    """ResNet50-based deepfake detection model"""
    
    def __init__(self, num_classes=2, pretrained=True):
        super(ResNetDeepfakeDetector, self).__init__()
        
        # Load pretrained ResNet50
        if pretrained:
            self.backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        else:
            self.backbone = resnet50(weights=None)
        
        # Replace the final layer
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_ftrs, num_classes)
        
    def forward(self, x):
        return nn.functional.softmax(self.backbone(x), dim=1)


class DeepfakeModel:
    """Main model class for deepfake detection"""
    
    def __init__(self, config=None):
        # Default configuration
        self.config = config or {
            'epochs': 10,
            'step_size': 10,
            'learning_rate': 0.001,
            'gamma': 0.1,
            'img_size': 224,
            'batch_size': 16,
            'num_classes': 2,
            'test_size': 0.2,
            'val_size': 0.5
        }
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        self.label_mapping = {}
        self.index_mapping = {}
        
    def create_dataframe(self, data_path, max_samples_per_class=5000):
        """Create dataframe from dataset directory with Train/Test/Validation structure"""
        data_dict = {"images": [], "labels": []}
        
        # Process each split (Train, Test, Validation)
        for split in ['Train', 'Test', 'Validation']:
            split_path = os.path.join(data_path, split)
            if not os.path.exists(split_path):
                print(f"Warning: {split} directory not found")
                continue
                
            # Process each class (Real, Fake) within the split
            for class_name in ['Real', 'Fake']:
                class_path = os.path.join(split_path, class_name)
                if not os.path.exists(class_path):
                    print(f"Warning: {class_name} directory not found in {split}")
                    continue
                
                sample_count = 0
                for img_file in os.listdir(class_path):
                    if sample_count >= max_samples_per_class:
                        break
                        
                    img_path = os.path.join(class_path, img_file)
                    if os.path.isfile(img_path) and img_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        data_dict["images"].append(img_path)
                        data_dict["labels"].append(class_name)
                        sample_count += 1
                
                print(f"Loaded {sample_count} {class_name} images from {split}")
        
        return pd.DataFrame(data_dict)
    
    def setup_label_mapping(self, df):
        """Setup label to index mapping"""
        unique_labels = df["labels"].unique()
        # Remove any NaN values
        unique_labels = [label for label in unique_labels if pd.notna(label)]
        
        self.index_mapping = {i: label for i, label in enumerate(unique_labels)}
        self.label_mapping = {label: i for i, label in enumerate(unique_labels)}
        
        print(f"Label mapping: {self.label_mapping}")
        return df
    
    def get_transforms(self):
        """Get image transforms for training"""
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor(),
            transforms.Resize((self.config['img_size'], self.config['img_size'])),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def prepare_data(self, data_path):
        """Prepare datasets and data loaders using existing Train/Test/Validation splits"""
        # Create separate dataframes for each split
        train_df = self.create_dataframe_from_split(data_path, 'Train')
        val_df = self.create_dataframe_from_split(data_path, 'Validation')
        test_df = self.create_dataframe_from_split(data_path, 'Test')
        
        # Setup label mapping using train data
        self.setup_label_mapping(train_df)
        
        # Apply label mapping to all splits
        train_df["labels"] = train_df["labels"].map(self.label_mapping)
        val_df["labels"] = val_df["labels"].map(self.label_mapping)
        test_df["labels"] = test_df["labels"].map(self.label_mapping)
        
        # Remove any rows with NaN labels
        train_df = train_df.dropna(subset=['labels'])
        val_df = val_df.dropna(subset=['labels'])
        test_df = test_df.dropna(subset=['labels'])
        
        print(f"Training samples: {len(train_df)}")
        print(f"Validation samples: {len(val_df)}")
        print(f"Test samples: {len(test_df)}")
        
        # Create datasets
        transform = self.get_transforms()
        train_dataset = DeepfakeDataset(train_df.values, transform)
        val_dataset = DeepfakeDataset(val_df.values, transform)
        test_dataset = DeepfakeDataset(test_df.values, transform)
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.config['batch_size'], 
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=self.config['batch_size'], 
            shuffle=False
        )
        test_loader = DataLoader(
            test_dataset, 
            batch_size=self.config['batch_size'], 
            shuffle=False
        )
        
        return train_loader, val_loader, test_loader
    
    def create_dataframe_from_split(self, data_path, split_name, max_samples_per_class=5000):
        """Create dataframe from a specific split (Train/Test/Validation)"""
        data_dict = {"images": [], "labels": []}
        split_path = os.path.join(data_path, split_name)
        
        print(f"Looking for split: {split_path}")
        print(f"Split exists: {os.path.exists(split_path)}")
        
        if not os.path.exists(split_path):
            print(f"Warning: {split_name} directory not found")
            return pd.DataFrame(data_dict)
        
        # Process each class (Real, Fake) within the split
        for class_name in ['Real', 'Fake']:
            class_path = os.path.join(split_path, class_name)
            if not os.path.exists(class_path):
                print(f"Warning: {class_name} directory not found in {split_name}")
                continue
            
            sample_count = 0
            for img_file in os.listdir(class_path):
                if sample_count >= max_samples_per_class:
                    break
                    
                img_path = os.path.join(class_path, img_file)
                if os.path.isfile(img_path) and img_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    data_dict["images"].append(img_path)
                    data_dict["labels"].append(class_name)
                    sample_count += 1
            
            print(f"Loaded {sample_count} {class_name} images from {split_name}")
        
        return pd.DataFrame(data_dict)
    
    def initialize_model(self):
        """Initialize the model, optimizer, and scheduler"""
        self.model = ResNetDeepfakeDetector(
            num_classes=self.config['num_classes']
        ).to(self.device)
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(
            self.model.parameters(), 
            lr=self.config['learning_rate']
        )
        self.scheduler = torch.optim.lr_scheduler.StepLR(
            self.optimizer, 
            step_size=self.config['step_size'], 
            gamma=self.config['gamma']
        )
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        # Create progress bar for training
        pbar = tqdm(train_loader, desc="Training", leave=False)
        
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
            
            # Update progress bar with current metrics
            current_acc = correct / total if total > 0 else 0
            pbar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Acc': f'{current_acc:.4f}'
            })
        
        return total_loss / len(train_loader), correct / total
    
    def validate(self, val_loader):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        # Create progress bar for validation
        pbar = tqdm(val_loader, desc="Validation", leave=False)
        
        with torch.no_grad():
            for data, target in pbar:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
                
                # Update progress bar with current metrics
                current_acc = correct / total if total > 0 else 0
                pbar.set_postfix({
                    'Loss': f'{loss.item():.4f}',
                    'Acc': f'{current_acc:.4f}'
                })
        
        return total_loss / len(val_loader), correct / total
    
    def train(self, data_path):
        """Main training function"""
        # Prepare data
        train_loader, val_loader, test_loader = self.prepare_data(data_path)
        
        # Initialize model
        self.initialize_model()
        
        # Training loop with progress bar
        train_losses = []
        val_losses = []
        train_accs = []
        val_accs = []
        
        # Create epoch progress bar
        epoch_pbar = tqdm(range(self.config['epochs']), desc="Training Progress", position=0)
        
        for epoch in epoch_pbar:
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = self.validate(val_loader)
            
            # Update scheduler
            self.scheduler.step()
            
            # Store metrics
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            train_accs.append(train_acc)
            val_accs.append(val_acc)
            
            # Update epoch progress bar
            epoch_pbar.set_postfix({
                'Train Acc': f'{train_acc:.4f}',
                'Val Acc': f'{val_acc:.4f}',
                'LR': f'{self.optimizer.param_groups[0]["lr"]:.6f}'
            })
            
            print(f'\nEpoch {epoch+1}/{self.config["epochs"]}:')
            print(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}')
            print(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')
            print(f'  Learning Rate: {self.optimizer.param_groups[0]["lr"]:.6f}')
            print('-' * 50)
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_accs': train_accs,
            'val_accs': val_accs,
            'test_loader': test_loader
        }
    
    def predict(self, image_path):
        """Predict on a single image"""
        if self.model is None:
            raise ValueError("Model not initialized. Call train() first.")
        
        self.model.eval()
        transform = self.get_transforms()
        
        # Load and preprocess image
        img = Image.open(image_path).convert("RGB")
        img = np.array(img)
        img = transform(img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(img)
            prediction = output.argmax(dim=1).item()
            confidence = output.max().item()
        
        return {
            'prediction': self.index_mapping[prediction],
            'confidence': confidence,
            'probabilities': output.cpu().numpy()[0]
        }
    
    def save_model(self, path):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'label_mapping': self.label_mapping,
            'index_mapping': self.index_mapping
        }, path)
    
    def load_model(self, path):
        """Load a trained model"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.config = checkpoint['config']
        self.label_mapping = checkpoint['label_mapping']
        self.index_mapping = checkpoint['index_mapping']
        
        self.initialize_model()
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        return self


if __name__ == "__main__":
    # Example usage
    model = DeepfakeModel({
        'epochs': 10,
        'step_size': 10,
        'learning_rate': 0.001,
        'gamma': 0.1,
        'img_size': 224,
        'batch_size': 16,
        'num_classes': 2
    })
    
    # Train the model with your dataset
    print("Starting training...")
    results = model.train("./Dataset")
    
    # Save the trained model
    model.save_model("deepfake_model.pth")
    print("Model saved successfully!")