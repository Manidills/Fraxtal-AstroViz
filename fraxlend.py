from io import StringIO
import streamlit as st
import pandas as pd
import requests
import json
from pyvis.network import Network
import tempfile

def get_user_positions_query(user_id):
    return f"""
    {{
      user(id: "{user_id}") {{
        address
        id
        positions(orderBy: depositedCollateralAmount) {{
          borrowedAssetShare
          dailyHistory {{
            lendDepositedAsset
            lendProfitTaken
          }}
          depositedCollateralAmount
          lentAssetShare
          timestamp
          block
        }}
      }}
    }}
    """

def get_pair_per_days_query(first, orderBy):
    return f"""
    {{
      pairPerDays(first: {first}, orderBy: {orderBy}, orderDirection: desc) {{
        exchangeRate
        feeToProtocolRate
        interestPerSecond
        protocolFeeValue
        protocolFeeWithdrawn
        protocolFeeWithdrawnValue
        protocolLiqFeeValue
        protocolLiqFeeWithdrawn
        protocolLiqFeeWithdrawnValue
        timestamp
        totalAssetAmount
        totalAssetShare
        totalAssetValue
        totalBorrowAmount
        totalBorrowShare
        totalFeesShare
        totalFeesAmount
        totalCollateralValue
        totalCollateral
        totalBorrowValue
        totalLiquidationFee
      }}
    }}
    """



# Function to create a GraphQL query for Fraxlend Factories
def create_factories_query(first, order_by, order_direction):
    return f"""
    {{
        fraxlendFactories(first: {first}, orderBy: {order_by}, orderDirection: {order_direction}) {{
            id
            pairCount
            assetTokenCount
            collateralTokenCount
            totalBorrowedValue
            totalCollateralLockedValue
            totalLiquidationFeeValue
            totalTVLValue
            totalProtocolFeeValue
        }}
        fraxlendFactoryPerDays(first: {first}, orderBy: {order_by}, orderDirection: {order_direction}) {{
            id
            fraxlendFactory {{
                id
                totalTVLValue
                totalProtocolFeeValue
                totalLiquidationFeeValue
                totalCollateralLockedValue
                totalBorrowedValue
                pairCount
            }}
            pairCount
            assetTokenCount
        }}
    }}
    """


# Function to create a GraphQL query for Liquidations
def create_liquidations_query(first, order_by, order_direction):
    return f"""
    {{
        liquidations(first: {first}, orderBy: {order_by}, orderDirection: {order_direction}) {{
            amountToAdjust
            block
            collateralTaken
            exchangeRate
            repayAmount
            repayShare
            sharesToAdjust
            timestamp
            id
            pair {{
                borrowerWhitelistActive
                cleanLiquidationFee
                dirtyLiquidationFee
            }}
        }}
    }}
    """


# Function to create a GraphQL query for Tokens
def create_tokens_query(first, order_by, order_direction):
    return f"""
    {{
        tokens(first: {first}, orderBy: {order_by}, orderDirection: {order_direction}) {{
            address
            decimals
            name
            pairAssetCount
            pairCollateralCount
            totalSupply
            symbol
            assetPairs {{
                address
                liquidationFee
                cleanLiquidationFee
                borrowerWhitelistActive
            }}
        }}
    }}
    """


# Function to fetch data from GraphQL endpoint
def fetch_data(query):
    url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/8G87c8NeUgFYsrHSgETW8GTJv6gF5NfzZ6szgkcMDH3J"
    response = requests.post(url, json={'query': query})
    return response.json()['data']


# Function to create network graph using pyvis
def create_network_graph(nodes, edges, height='750px'):
    net = Network(height=height, width='100%', bgcolor='#ffffff', font_color='black')
    for node in nodes:
        net.add_node(node['id'], label=node['label'], title=node['title'])
    for edge in edges:
        net.add_edge(edge['source'], edge['target'])

    # Customize other settings as needed
    net.repulsion(node_distance=500, spring_length=400)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
        net.write_html(temp_file.name)
        temp_file.seek(0)
        html_content = temp_file.read().decode("utf-8")
    return html_content


# Function to render the Streamlit app for Fraxlend Factories
def render_fraxlend_factories_app():
    st.markdown("### Select Fraxlend Factories Options")
    first = st.number_input("First", min_value=1, value=5)
    order_by = st.selectbox("Order By", ["totalTVLValue", "totalBorrowedValue", "totalCollateralLockedValue"])
    order_direction = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = create_factories_query(first, order_by, order_direction)
        data = fetch_data(query)

        factories_df = pd.json_normalize(data['fraxlendFactories'])
        factories_per_days_df = pd.json_normalize(data['fraxlendFactoryPerDays'])

        st.write("Fraxlend Factories Data")
        st.dataframe(factories_df)

        st.write("Fraxlend Factory Per Days Data")
        st.dataframe(factories_per_days_df)

        st.write("Network Explorer")
        nodes = [{'id': factory_day['id'], 'label': f"Day: {factory_day['id']}", 'title': f"Factory Day: {factory_day['id']}"} for factory_day in data['fraxlendFactoryPerDays']]
        edges = []
        for factory_day in data['fraxlendFactoryPerDays']:
            factory_id = factory_day['fraxlendFactory']['id']
            factory_day_id = factory_day['id']
            edges.extend([
                {'source': factory_day_id, 'target': factory_id},
                {'source': factory_day_id, 'target': f"Pairs: {factory_day['pairCount']}"},
                {'source': factory_day_id, 'target': f"Assets: {factory_day['assetTokenCount']}"},
                {'source': factory_day_id, 'target': f"Borrowed: {factory_day['fraxlendFactory']['totalBorrowedValue']}"},
                {'source': factory_day_id, 'target': f"Collateral Locked: {factory_day['fraxlendFactory']['totalCollateralLockedValue']}"},
                {'source': factory_day_id, 'target': f"Liquidation Fee: {factory_day['fraxlendFactory']['totalLiquidationFeeValue']}"},
                {'source': factory_day_id, 'target': f"Protocol Fee: {factory_day['fraxlendFactory']['totalProtocolFeeValue']}"},
                {'source': factory_day_id, 'target': f"TVL: {factory_day['fraxlendFactory']['totalTVLValue']}"}
            ])
            nodes.extend([
                {'id': factory_id, 'label': f"Factory: {factory_id}", 'title': ''},
                {'id': f"Pairs: {factory_day['pairCount']}", 'label': f"Pairs: {factory_day['pairCount']}", 'title': ''},
                {'id': f"Assets: {factory_day['assetTokenCount']}", 'label': f"Assets: {factory_day['assetTokenCount']}", 'title': ''},
                {'id': f"Borrowed: {factory_day['fraxlendFactory']['totalBorrowedValue']}", 'label': f"Borrowed: {factory_day['fraxlendFactory']['totalBorrowedValue']}", 'title': ''},
                {'id': f"Collateral Locked: {factory_day['fraxlendFactory']['totalCollateralLockedValue']}", 'label': f"Collateral Locked: {factory_day['fraxlendFactory']['totalCollateralLockedValue']}", 'title': ''},
                {'id': f"Liquidation Fee: {factory_day['fraxlendFactory']['totalLiquidationFeeValue']}", 'label': f"Liquidation Fee: {factory_day['fraxlendFactory']['totalLiquidationFeeValue']}", 'title': ''},
                {'id': f"Protocol Fee: {factory_day['fraxlendFactory']['totalProtocolFeeValue']}", 'label': f"Protocol Fee: {factory_day['fraxlendFactory']['totalProtocolFeeValue']}", 'title': ''},
                {'id': f"TVL: {factory_day['fraxlendFactory']['totalTVLValue']}", 'label': f"TVL: {factory_day['fraxlendFactory']['totalTVLValue']}", 'title': ''}
            ])

        html_content = create_network_graph(nodes, edges)
        st.components.v1.html(html_content, height=800)


# Function to render the Streamlit app for Liquidations
def render_liquidations_app():
    st.markdown("### Select Liquidations Options")
    first = st.number_input("First", min_value=1, value=5)
    order_by = st.selectbox("Order By", ["repayAmount", "repayShare"])
    order_direction = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = create_liquidations_query(first, order_by, order_direction)
        data = fetch_data(query)

        st.dataframe(data['liquidations'])

        st.write("Network Explorer")
        nodes = [{'id': liquidation['id'], 'label': f"Liquidation: {liquidation['id']}", 'title': f"Liquidation ID: {liquidation['id']}"} for liquidation in data['liquidations']]
        edges = []
        for liquidation in data['liquidations']:
            liquidation_id = liquidation['id']
            edges.extend([
                {'source': liquidation_id, 'target': f"Amount to Adjust: {liquidation['amountToAdjust']}"},
                {'source': liquidation_id, 'target': f"Block: {liquidation['block']}"},
                {'source': liquidation_id, 'target': f"Collateral Taken: {liquidation['collateralTaken']}"},
                {'source': liquidation_id, 'target': f"Exchange Rate: {liquidation['exchangeRate']}"},
                {'source': liquidation_id, 'target': f"Repay Amount: {liquidation['repayAmount']}"},
                {'source': liquidation_id, 'target': f"Repay Share: {liquidation['repayShare']}"},
                {'source': liquidation_id, 'target': f"Shares to Adjust: {liquidation['sharesToAdjust']}"},
                {'source': liquidation_id, 'target': f"Timestamp: {liquidation['timestamp']}"},
                {'source': liquidation_id, 'target': f"Borrower Whitelist Active: {liquidation['pair']['borrowerWhitelistActive']}"},
                {'source': liquidation_id, 'target': f"Clean Liquidation Fee: {liquidation['pair']['cleanLiquidationFee']}"},
                {'source': liquidation_id, 'target': f"Dirty Liquidation Fee: {liquidation['pair']['dirtyLiquidationFee']}"}
            ])
            nodes.extend([
                {'id': f"Amount to Adjust: {liquidation['amountToAdjust']}", 'label': f"Amount to Adjust: {liquidation['amountToAdjust']}", 'title': ''},
                {'id': f"Block: {liquidation['block']}", 'label': f"Block: {liquidation['block']}", 'title': ''},
                {'id': f"Collateral Taken: {liquidation['collateralTaken']}", 'label': f"Collateral Taken: {liquidation['collateralTaken']}", 'title': ''},
                {'id': f"Exchange Rate: {liquidation['exchangeRate']}", 'label': f"Exchange Rate: {liquidation['exchangeRate']}", 'title': ''},
                {'id': f"Repay Amount: {liquidation['repayAmount']}", 'label': f"Repay Amount: {liquidation['repayAmount']}", 'title': ''},
                {'id': f"Repay Share: {liquidation['repayShare']}", 'label': f"Repay Share: {liquidation['repayShare']}", 'title': ''},
                {'id': f"Shares to Adjust: {liquidation['sharesToAdjust']}", 'label': f"Shares to Adjust: {liquidation['sharesToAdjust']}", 'title': ''},
                {'id': f"Timestamp: {liquidation['timestamp']}", 'label': f"Timestamp: {liquidation['timestamp']}", 'title': ''},
                {'id': f"Borrower Whitelist Active: {liquidation['pair']['borrowerWhitelistActive']}", 'label': f"Borrower Whitelist Active: {liquidation['pair']['borrowerWhitelistActive']}", 'title': ''},
                {'id': f"Clean Liquidation Fee: {liquidation['pair']['cleanLiquidationFee']}", 'label': f"Clean Liquidation Fee: {liquidation['pair']['cleanLiquidationFee']}", 'title': ''},
                {'id': f"Dirty Liquidation Fee: {liquidation['pair']['dirtyLiquidationFee']}", 'label': f"Dirty Liquidation Fee: {liquidation['pair']['dirtyLiquidationFee']}", 'title': ''}
            ])

        html_content = create_network_graph(nodes, edges)
        st.components.v1.html(html_content, height=800)


# Function to render the Streamlit app for Tokens
def render_tokens_app():
    st.markdown("### Select Tokens Options")
    first = st.number_input("First", min_value=1, value=5)
    order_by = st.selectbox("Order By", ["totalSupply", "pairAssetCount"])
    order_direction = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = create_tokens_query(first, order_by, order_direction)
        data = fetch_data(query)

        st.dataframe(data['tokens'])

        st.write("Network Explorer")
        nodes = [{'id': token['address'], 'label': f"Token: {token['symbol']}", 'title': f"Token Name: {token['name']}"} for token in data['tokens']]
        edges = []
        for token in data['tokens']:
            token_id = token['address']
            edges.extend([
                {'source': token_id, 'target': f"Decimals: {token['decimals']}"},
                {'source': token_id, 'target': f"Pair Asset Count: {token['pairAssetCount']}"},
                {'source': token_id, 'target': f"Pair Collateral Count: {token['pairCollateralCount']}"},
                {'source': token_id, 'target': f"Total Supply: {token['totalSupply']}"}
            ])
            nodes.extend([
                {'id': f"Decimals: {token['decimals']}", 'label': f"Decimals: {token['decimals']}", 'title': ''},
                {'id': f"Pair Asset Count: {token['pairAssetCount']}", 'label': f"Pair Asset Count: {token['pairAssetCount']}", 'title': ''},
                {'id': f"Pair Collateral Count: {token['pairCollateralCount']}", 'label': f"Pair Collateral Count: {token['pairCollateralCount']}", 'title': ''},
                {'id': f"Total Supply: {token['totalSupply']}", 'label': f"Total Supply: {token['totalSupply']}", 'title': ''}
            ])
            for pair in token['assetPairs']:
                pair_id = pair['address']
                nodes.append({'id': pair_id, 'label': f"Asset Pair: {pair_id}", 'title': f"Asset Pair Address: {pair_id}"})
                edges.extend([
                    {'source': token_id, 'target': pair_id},
                    {'source': pair_id, 'target': f"Liquidation Fee: {pair['liquidationFee']}"},
                    {'source': pair_id, 'target': f"Clean Liquidation Fee: {pair['cleanLiquidationFee']}"},
                    {'source': pair_id, 'target': f"Borrower Whitelist Active: {pair['borrowerWhitelistActive']}"}
                ])
                nodes.extend([
                    {'id': f"Liquidation Fee: {pair['liquidationFee']}", 'label': f"Liquidation Fee: {pair['liquidationFee']}", 'title': ''},
                    {'id': f"Clean Liquidation Fee: {pair['cleanLiquidationFee']}", 'label': f"Clean Liquidation Fee: {pair['cleanLiquidationFee']}", 'title': ''},
                    {'id': f"Borrower Whitelist Active: {pair['borrowerWhitelistActive']}", 'label': f"Borrower Whitelist Active: {pair['borrowerWhitelistActive']}", 'title': ''}
                ])

        html_content = create_network_graph(nodes, edges)
        st.components.v1.html(html_content, height=800)


def pairs():
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = ["totalAssetAmount", "totalBorrowAmount", "totalCollateralValue", "totalLiquidationFee"]
    orderBy = st.selectbox("Order By", options=orderBy_options)
    
    # Execute GraphQL query
    query = get_pair_per_days_query(first, orderBy)
    data = fetch_data(query)

    st.dataframe(data['pairPerDays'])
    
    nodes = []
    edges = []
    
    for pair_data in data['pairPerDays']:
        timestamp = pair_data['timestamp']
        total_asset_amount = pair_data['totalAssetAmount']
        total_borrow_amount = pair_data['totalBorrowAmount']
        total_collateral_value = pair_data['totalCollateralValue']
        total_liquidation_fee = pair_data['totalLiquidationFee']
        
        nodes.extend([
            {'id': f"Timestamp: {timestamp}", 'label': f"Timestamp: {timestamp}", 'title': ''},
            {'id': f"Total Asset Amount: {total_asset_amount}", 'label': f"Total Asset Amount: {total_asset_amount}", 'title': ''},
            {'id': f"Total Borrow Amount: {total_borrow_amount}", 'label': f"Total Borrow Amount: {total_borrow_amount}", 'title': ''},
            {'id': f"Total Collateral Value: {total_collateral_value}", 'label': f"Total Collateral Value: {total_collateral_value}", 'title': ''},
            {'id': f"Total Liquidation Fee: {total_liquidation_fee}", 'label': f"Total Liquidation Fee: {total_liquidation_fee}", 'title': ''}
        ])
        
        edges.extend([
            {'source': f"Timestamp: {timestamp}", 'target': f"Total Asset Amount: {total_asset_amount}"},
            {'source': f"Timestamp: {timestamp}", 'target': f"Total Borrow Amount: {total_borrow_amount}"},
            {'source': f"Timestamp: {timestamp}", 'target': f"Total Collateral Value: {total_collateral_value}"},
            {'source': f"Timestamp: {timestamp}", 'target': f"Total Liquidation Fee: {total_liquidation_fee}"}
        ])
    
    
    # Create and display network graph
    st.write("Network Explorer")
    html_content = create_network_graph(nodes, edges)
    st.components.v1.html(html_content, height=800)


def user():
    # Input user ID
    user_id = st.text_input("Enter User ID (e.g., 0xffd54abe15c68d36f6932210ab3225e05c6d1e09):")

    # Execute GraphQL query on button click
    if st.button("Fetch Data"):
        st.markdown("## Network Explorer")
        
        try:
            # Execute GraphQL query
            query = get_user_positions_query(user_id)
            data = fetch_data(query)

            st.dataframe(data['user'])

            # Prepare nodes and edges for network graph
            nodes = []
            edges = []

            if data and 'user' in data:
                user_data = data['user']
                positions = user_data['positions']

                # Create nodes for positions
                for idx, position in enumerate(positions):
                    node_id = f"Position_{idx + 1}"
                    label = f"Position {idx + 1}\nTimestamp: {position['timestamp']}\nCollateral: {position['depositedCollateralAmount']}"
                    nodes.append({'id': node_id, 'label': label, 'title': f"Position {idx + 1}"})

                # Create edges between positions
                if len(positions) > 1:
                    for i in range(len(positions) - 1):
                        source_node = f"Position_{i + 1}"
                        target_node = f"Position_{i + 2}"
                        edges.append({'source': source_node, 'target': target_node})

                # Generate and display network graph HTML
                html_content = create_network_graph(nodes, edges)
                st.components.v1.html(html_content, height=800)
            else:
                st.write("No data found for the user.")
        
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")


# Main function to run the Streamlit app
def lend():
    st.title('Fraxlend Explorer')
    st.markdown("### Select an Option")
    option = st.radio(
        "Select Choice",
        ("Fraxlend Factories", "Liquidations", "Tokens", "User", "Pair Per Days"),
        index=0,
        horizontal=True
    )

    if option == 'Fraxlend Factories':
        render_fraxlend_factories_app()
    elif option == 'Liquidations':
        render_liquidations_app()
    elif option == 'Tokens':
        render_tokens_app()
    elif option == 'User':
        user()
    elif option == 'Pair Per Days':
        pairs()
