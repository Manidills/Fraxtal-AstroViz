import base64
import io
import os
import PyPDF2
import tempfile
from PIL import Image
from explorer.near import near_app
from fraxbridge import Bridge
from fraxethstack import staking
from fraxlend import lend
from fraxswap import swap
import streamlit as st
import requests
from wallet_connect import wallet_connect
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import io


st.set_page_config(
    page_title="DataVista-AI",
    page_icon="❄️️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This app generates scripts for data clean rooms!"
    }
)


st.sidebar.image("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDFjb2UzaWFwMnZqZWE1b2N3Yjc5OTltYzdxM2h5YXY2MWd6MXBxbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/UAragLbg9oKRfZLThq/giphy.webp")
action = st.sidebar.radio("What action would you like to take?", ("Analytics","FraxSwap", "FraxLend","FraxEthStaking","FraxBridging"))

def wallet_con():
    with st.sidebar:
        st.markdown('##')
        wallet =  wallet_connect(
            label="login", 
            key="login", 
            message="Login", 
            auth_token_contract_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            chain_name="ethereum", 
            contract_type="ERC20",
            num_tokens="0"
            )
        return wallet
    


if action == "Analytics":
    near_app()
elif action == "FraxLend":
    lend()
elif action == "FraxSwap":
    swap()
elif action == "FraxEthStaking":
    staking()
elif action == "FraxBridging":
    Bridge()