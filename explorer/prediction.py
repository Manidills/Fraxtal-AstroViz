import asyncio
import yfinance as yf
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
import streamlit as st
import matplotlib.pyplot as plt
import datetime as dt
import altair as alt
import sys





    

# Step 1: Fetch Historical Price Data
def fetch_data(ticker, start_date):
    data = yf.download(ticker, start=start_date)
    return data['Close'].values.reshape(-1, 1)

# Step 2: Preprocess Data
def preprocess_data(data, window_size):
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    X = []
    y = []
    for i in range(window_size, len(data_scaled)):
        X.append(data_scaled[i-window_size:i, 0])
        y.append(data_scaled[i, 0])
    
    X = np.array(X)
    y = np.array(y)
    
    return X, y, scaler

# Step 3: Build the Neural Network Model
class PricePredictor(nn.Module):
    def __init__(self, input_size):
        super(PricePredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, 50)
        self.fc2 = nn.Linear(50, 25)
        self.fc3 = nn.Linear(25, 1)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Step 4: Train the Model
def train_model(model, dataloader, criterion, optimizer, epochs=50):
    model.train()
    for epoch in range(epochs):
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

# Step 5: Predict the Next Price
def predict_next_price(model, data, window_size, scaler):
    model.eval()
    last_window = data[-window_size:]
    last_window_scaled = scaler.transform(last_window)
    last_window_scaled = torch.tensor(last_window_scaled, dtype=torch.float32).view(1, -1)
    
    with torch.no_grad():
        predicted_price_scaled = model(last_window_scaled)
    
    predicted_price = scaler.inverse_transform(predicted_price_scaled.numpy().reshape(-1, 1))
    return predicted_price[0, 0]

# Step 6: Convert Model to ONNX
def serialize_to_onnx(model, input_size, onnx_file_path):
    model.eval()
    dummy_input = torch.randn(1, input_size)
    torch.onnx.export(model, dummy_input, onnx_file_path,
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
    print(f"✅ Model has been converted to ONNX and saved at {onnx_file_path} ")

def get_near_data(start_date, end_date):
    near = yf.Ticker("FXS-USD")
    return near.history(start=start_date, end=end_date)

# Main execution
def pred():


    start_date = st.date_input("Start Date", value=pd.to_datetime('2023-01-01'))
    end_date = st.date_input("End Date", value=pd.to_datetime('today'))

    st.write(""" ## Cryptocurrency Price Visualizer """)

    crypto_name = st.selectbox("Select Cryptcurrency",("FXS", "BTC"))
    currency_name = st.selectbox("Select Local Currency",("USD","EUR","INR","CAD","AUD","GBP"))

    if st.button("Visualize"):


        data = get_near_data(start_date,end_date)
        # data = web.DataReader(f"{crypto_name}-{currency_name}", "yahoo")
        # st.write(pd.DataFrame(data))
        st.write(f"Ploting the graph between {crypto_name} and {currency_name}.")

        s = data['Close'].tail(1) 
        st.write(f"The closing price for the {crypto_name} is {s} ")

        st.markdown("##")
        data = data.reset_index()
        data['Date'] = pd.to_datetime(data.Date, errors='coerce')
        st.altair_chart(
        alt.Chart(data).mark_line(color='blue').encode(
            y=alt.Y('Close:N', sort='descending'),
            x=alt.X('Date:T', sort='ascending'),
        ).properties(
        width=800,
        height=300
        ),  use_container_width=True
        )

        # Parameters
        
        ticker_pair = f"{crypto_name}-{currency_name}"
        ticker = ticker_pair
        start_date = "2020-01-01"
        window_size = 60
        batch_size = 32
        epochs = 50



        
        # Fetch and preprocess data
        print("Fetching and preprocessing data...")
        #data = fetch_data(ticker, start_date)
        data_1 = get_near_data(start_date,end_date)
        data = data_1['Close'].values.reshape(-1, 1)
        X, y, scaler = preprocess_data(data, window_size)
        
        # Convert to PyTorch tensors
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)
        
        # Create DataLoader
        print("Creating DataLoader...")
        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Build and train model
        print("Building and training model...")
        model = PricePredictor(X_tensor.shape[1])
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        train_model(model, dataloader, criterion, optimizer, epochs=epochs)
        
        # Predict the next price
        st.info("Predicting the next price...")
        next_price = predict_next_price(model, data, window_size, scaler)
        st.success(f"Predicted next price of {crypto_name}-{currency_name}: {next_price}")






