import pickle
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import random

from src.metro import moscow_metro_stations

class ApartmentPriceNet(nn.Module):
    def __init__(self, input_dim):
        super(ApartmentPriceNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.model(x)


def predict_apartment_price(
    area: float,
    number_of_rooms: int,
    living_area: float| None = None,
    kitchen_area: float | None = None,
    minutes_to_metro: int | None = None,
    number_of_floors: int | None = None,
    floor: int | None = None,
    apartment_type: str | None = None,
    metro_station: str | None = None,
    renovation: str = 'European-style renovation',
    region: str = 'Moscow region',
    model_path: str ='models/model.pth',
    scaler_x_path: str ='models/scaler_x.pkl',
    scaler_y_path: str ='models/scaler_y.pkl',
    encoder_path: str ='models/encoder_cat.pkl'
):
    """
    Предсказывает стоимость квартиры на основе параметров.
    
    Args:
        area (float): Общая площадь квартиры (м²)
        living_area (float): Жилая площадь (м²)
        kitchen_area (float): Площадь кухни (м²)
        number_of_rooms (int): Количество комнат
        minutes_to_metro (float): Минут до метро
        number_of_floors (int): Этажность дома
        floor (int): Этаж квартиры
        apartment_type (str): 'Primary' или 'Secondary'
        metro_station (str): Название станции метро
        region (str): 'Moscow' или 'Moscow region'
        renovation (str): Тип ремонта
        model_path (str): Путь к файлу модели
        scaler_x_path (str): Путь к scaler для числовых признаков
        scaler_y_path (str): Путь к scaler для цены
        encoder_path (str): Путь к OneHotEncoder
    
    Returns:
        dict: Словарь с предсказанной ценой и информацией
    """

    if not living_area:
        living_area = random.uniform(0, area)
    
    if not kitchen_area:
        kitchen_area = random.uniform(0, area - living_area)

    if not number_of_floors:
        number_of_floors = random.randint(1, 50)
    
    if not floor:
        floor = random.randint(1, number_of_floors)

    if not minutes_to_metro:
        minutes_to_metro = random.randint(1, 30)

    if not apartment_type:
        apartment_type = random.choice(['Primary', 'Secondary'])

    if not metro_station:
        metro_station = random.choice(moscow_metro_stations)

    try:
        with open(scaler_x_path, 'rb') as f:
            scaler_x = pickle.load(f)
        with open(scaler_y_path, 'rb') as f:
            scaler_y = pickle.load(f)
        with open(encoder_path, 'rb') as f:
            encoder_cat = pickle.load(f)
        
        numerical_features = ['Area', 'Living area', 'Kitchen area', 'Number of rooms', 
                            'Minutes to metro', 'Number of floors', 'Floor']
        categorical_features = ['Apartment type', 'Metro station', 'Region', 'Renovation']
        
        input_dim = len(numerical_features) + len(encoder_cat.get_feature_names_out(categorical_features))
        model = ApartmentPriceNet(input_dim)
        model.load_state_dict(torch.load(model_path, weights_only=True))
        model.eval()
        
        data = pd.DataFrame({
            'Area': [area],
            'Living area': [living_area],
            'Kitchen area': [kitchen_area],
            'Number of rooms': [number_of_rooms],
            'Minutes to metro': [minutes_to_metro],
            'Number of floors': [number_of_floors],
            'Floor': [floor],
            'Apartment type': [apartment_type],
            'Metro station': [metro_station],
            'Region': [region],
            'Renovation': [renovation]
        })
        
        X_numeric = data[numerical_features].copy()
        X_numeric_scaled = scaler_x.transform(X_numeric)
        
        X_categorical = data[categorical_features].copy()
        X_categorical_encoded = encoder_cat.transform(X_categorical)
        
        X_processed = np.hstack([X_numeric_scaled, X_categorical_encoded])

        X_tensor = torch.tensor(X_processed, dtype=torch.float32)
        
        with torch.no_grad():
            predicted_scaled = model(X_tensor).numpy()
            predicted_price = scaler_y.inverse_transform(predicted_scaled)[0][0]
        
        return {
            'predicted_price': round(predicted_price, 2),
            'formatted_price': f"{predicted_price:,.0f} ₽",
            'apartment_params': {
                'area': area,
                'living_area': living_area,
                'kitchen_area': kitchen_area,
                'rooms': number_of_rooms,
                'metro_minutes': minutes_to_metro,
                'floor': floor,
                'building_floors': number_of_floors,
                'type': apartment_type,
                'metro': metro_station,
                'region': region,
                'renovation': renovation
            }
        }
        
    except FileNotFoundError as err:
        return {'error': f'Файл не найден: {err.filename}. Убедитесь, что сохранили модель!'}
    except Exception as err:
        return {'error': f'Ошибка: {str(err)}'}

