from io import StringIO
import streamlit as st
import pandas as pd
import requests
import json
from pyvis.network import Network
import pyvis.network as net
import tempfile

def create_fraxswap_network_graph():
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By",["totalVolumeETH", "dailyVolumeUSD", "totalLiquidityUSD", "totalLiquidityETH"])
    submit_button = st.button('Submit')
    if submit_button:
        query = f"""
        {{
        fraxswapDayDatas(first: {first}, orderBy: {orderBy_options}, orderDirection: desc) {{
            dailyVolumeETH
            dailyVolumeUSD
            dailyVolumeUntracked
            date
            id
            longTermOrderCount
            totalLiquidityETH
            totalLiquidityUSD
            totalVolumeETH
            totalVolumeUSD
            txCount
        }}
        }}
        """
        
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/3AMhp8Ck6ZScMibA8jfLhWFA9fKH6Zi8fMPHtb74Vsxv"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data_ = response.json()['data']
            st.dataframe(data_['fraxswapDayDatas'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        nodes = []
        edges = []

        for day_data in data_['fraxswapDayDatas']:
            day_id = day_data['id']
            date = day_data['date']
            daily_volume_eth = day_data['dailyVolumeETH']
            daily_volume_usd = day_data['dailyVolumeUSD']
            total_liquidity_eth = day_data['totalLiquidityETH']
            total_liquidity_usd = day_data['totalLiquidityUSD']
            total_volume_eth = day_data['totalVolumeETH']
            total_volume_usd = day_data['totalVolumeUSD']
            tx_count = day_data['txCount']

            nodes.extend([
                {'id': f"Day ID: {day_id}", 'label': f"Day ID: {day_id}", 'title': ''},
                {'id': f"Date: {date}", 'label': f"Date: {date}", 'title': ''},
                {'id': f"Daily Volume ETH: {daily_volume_eth}", 'label': f"Daily Volume ETH: {daily_volume_eth}", 'title': ''},
                {'id': f"Daily Volume USD: {daily_volume_usd}", 'label': f"Daily Volume USD: {daily_volume_usd}", 'title': ''},
                {'id': f"Total Liquidity ETH: {total_liquidity_eth}", 'label': f"Total Liquidity ETH: {total_liquidity_eth}", 'title': ''},
                {'id': f"Total Liquidity USD: {total_liquidity_usd}", 'label': f"Total Liquidity USD: {total_liquidity_usd}", 'title': ''},
                {'id': f"Total Volume ETH: {total_volume_eth}", 'label': f"Total Volume ETH: {total_volume_eth}", 'title': ''},
                {'id': f"Total Volume USD: {total_volume_usd}", 'label': f"Total Volume USD: {total_volume_usd}", 'title': ''},
                {'id': f"Transaction Count: {tx_count}", 'label': f"Transaction Count: {tx_count}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Day ID: {day_id}", 'target': f"Date: {date}"},
                {'source': f"Day ID: {day_id}", 'target': f"Daily Volume ETH: {daily_volume_eth}"},
                {'source': f"Day ID: {day_id}", 'target': f"Daily Volume USD: {daily_volume_usd}"},
                {'source': f"Day ID: {day_id}", 'target': f"Total Liquidity ETH: {total_liquidity_eth}"},
                {'source': f"Day ID: {day_id}", 'target': f"Total Liquidity USD: {total_liquidity_usd}"},
                {'source': f"Day ID: {day_id}", 'target': f"Total Volume ETH: {total_volume_eth}"},
                {'source': f"Day ID: {day_id}", 'target': f"Total Volume USD: {total_volume_usd}"},
                {'source': f"Day ID: {day_id}", 'target': f"Transaction Count: {tx_count}"}
            ])

        graph = net.Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        
        graph.repulsion(node_distance=300, spring_length=400)
    
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content
        


def create_fraxswap_factories_network_graph():
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By",["totalVolumeUSD", "totalLiquidityETH", "totalLiquidityUSD", "totalVolumeETH"])
    submit_button = st.button('Submit')
    if submit_button:
        query = f"""
        {{
        fraxswapFactories(first: {first}, orderBy: {orderBy_options}, orderDirection: desc) {{
            id
            pairCount
            totalVolumeUSD
            totalVolumeETH
            longTermOrderCount
            totalLiquidityETH
            totalLiquidityUSD
            txCount
            untrackedVolumeUSD
        }}
        }}
        """
        
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/3AMhp8Ck6ZScMibA8jfLhWFA9fKH6Zi8fMPHtb74Vsxv"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['fraxswapFactories'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        nodes = []
        edges = []

        for factory_data in data['fraxswapFactories']:
            factory_id = factory_data['id']
            pair_count = factory_data['pairCount']
            total_volume_usd = factory_data['totalVolumeUSD']
            total_volume_eth = factory_data['totalVolumeETH']
            long_term_order_count = factory_data['longTermOrderCount']
            total_liquidity_eth = factory_data['totalLiquidityETH']
            total_liquidity_usd = factory_data['totalLiquidityUSD']
            tx_count = factory_data['txCount']
            untracked_volume_usd = factory_data['untrackedVolumeUSD']

            nodes.extend([
                {'id': f"Factory ID: {factory_id}", 'label': f"Factory ID: {factory_id}", 'title': ''},
                {'id': f"Pair Count: {pair_count}", 'label': f"Pair Count: {pair_count}", 'title': ''},
                {'id': f"Total Volume USD: {total_volume_usd}", 'label': f"Total Volume USD: {total_volume_usd}", 'title': ''},
                {'id': f"Total Volume ETH: {total_volume_eth}", 'label': f"Total Volume ETH: {total_volume_eth}", 'title': ''},
                {'id': f"Long Term Order Count: {long_term_order_count}", 'label': f"Long Term Order Count: {long_term_order_count}", 'title': ''},
                {'id': f"Total Liquidity ETH: {total_liquidity_eth}", 'label': f"Total Liquidity ETH: {total_liquidity_eth}", 'title': ''},
                {'id': f"Total Liquidity USD: {total_liquidity_usd}", 'label': f"Total Liquidity USD: {total_liquidity_usd}", 'title': ''},
                {'id': f"Transaction Count: {tx_count}", 'label': f"Transaction Count: {tx_count}", 'title': ''},
                {'id': f"Untracked Volume USD: {untracked_volume_usd}", 'label': f"Untracked Volume USD: {untracked_volume_usd}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Factory ID: {factory_id}", 'target': f"Pair Count: {pair_count}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Total Volume USD: {total_volume_usd}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Total Volume ETH: {total_volume_eth}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Long Term Order Count: {long_term_order_count}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Total Liquidity ETH: {total_liquidity_eth}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Total Liquidity USD: {total_liquidity_usd}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Transaction Count: {tx_count}"},
                {'source': f"Factory ID: {factory_id}", 'target': f"Untracked Volume USD: {untracked_volume_usd}"}
            ])

        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content


def create_tokens_network_graph():
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=5)
    orderBy_options = st.selectbox("Order By",["tradeVolumeUSD", "totalLiquidity", "tradeVolume", "txCount"])
    submit_button = st.button('Submit')
    
    if submit_button:
        query = f"""
        {{
        tokens(first: {first}, orderBy: {orderBy_options}, orderDirection: desc) {{
            id
            symbol
            name
            decimals
            derivedETH
            totalLiquidity
            totalSupply
            tradeVolume
            tradeVolumeUSD
            txCount
            untrackedVolumeUSD
        }}
        }}
        """
        
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/3AMhp8Ck6ZScMibA8jfLhWFA9fKH6Zi8fMPHtb74Vsxv"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            #st.write(response.json())
            data = response.json()['data']
            st.dataframe(data['tokens'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        nodes = []
        edges = []

        for token_data in data['tokens']:
            token_id = token_data['id']
            symbol = token_data['symbol']
            name = token_data['name']
            decimals = token_data['decimals']
            total_liquidity = token_data['totalLiquidity']
            total_supply = token_data['totalSupply']
            trade_volume = token_data['tradeVolume']
            trade_volume_usd = token_data['tradeVolumeUSD']
            tx_count = token_data['txCount']
            untracked_volume_usd = token_data['untrackedVolumeUSD']

            nodes.extend([
                {'id': f"Token ID: {token_id}", 'label': f"{symbol} - {name}", 'title': ''},
                {'id': f"Decimals: {decimals}", 'label': f"Decimals: {decimals}", 'title': ''},
                {'id': f"Total Liquidity: {total_liquidity}", 'label': f"Total Liquidity: {total_liquidity}", 'title': ''},
                {'id': f"Total Supply: {total_supply}", 'label': f"Total Supply: {total_supply}", 'title': ''},
                {'id': f"Trade Volume: {trade_volume}", 'label': f"Trade Volume: {trade_volume}", 'title': ''},
                {'id': f"Trade Volume USD: {trade_volume_usd}", 'label': f"Trade Volume USD: {trade_volume_usd}", 'title': ''},
                {'id': f"Transaction Count: {tx_count}", 'label': f"Transaction Count: {tx_count}", 'title': ''},
                {'id': f"Untracked Volume USD: {untracked_volume_usd}", 'label': f"Untracked Volume USD: {untracked_volume_usd}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Token ID: {token_id}", 'target': f"Decimals: {decimals}"},
                {'source': f"Token ID: {token_id}", 'target': f"Total Liquidity: {total_liquidity}"},
                {'source': f"Token ID: {token_id}", 'target': f"Total Supply: {total_supply}"},
                {'source': f"Token ID: {token_id}", 'target': f"Trade Volume: {trade_volume}"},
                {'source': f"Token ID: {token_id}", 'target': f"Trade Volume USD: {trade_volume_usd}"},
                {'source': f"Token ID: {token_id}", 'target': f"Transaction Count: {tx_count}"},
                {'source': f"Token ID: {token_id}", 'target': f"Untracked Volume USD: {untracked_volume_usd}"}
            ])

        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show_buttons(filter_=['physics'])
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content
    

def create_swaps_network_graph():
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["amountUSD", "timestamp", "amount0In", "amount0Out", "amount1In", "amount1Out"])
    submit_button = st.button('Submit')
    
    if submit_button:
        query = f"""
        {{
        swaps(first: {first}, orderBy: {orderBy_options}, orderDirection: desc) {{
            amount0In
            amount0Out
            amount1In
            amount1Out
            amountUSD
            from
            id
            sender
            timestamp
            to
        }}
        }}
        """
        
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/3AMhp8Ck6ZScMibA8jfLhWFA9fKH6Zi8fMPHtb74Vsxv"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['swaps'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        nodes = []
        edges = []

        for swap in data['swaps']:
            swap_id = swap['id']
            amount0_in = swap['amount0In']
            amount0_out = swap['amount0Out']
            amount1_in = swap['amount1In']
            amount1_out = swap['amount1Out']
            amount_usd = swap['amountUSD']
            sender = swap['sender']
            receiver = swap['to']

            nodes.extend([
                {'id': f"Swap ID: {swap_id}", 'label': f"Swap ID: {swap_id}", 'title': ''},
                {'id': f"Amount 0 In: {amount0_in}", 'label': f"Amount 0 In: {amount0_in}", 'title': ''},
                {'id': f"Amount 0 Out: {amount0_out}", 'label': f"Amount 0 Out: {amount0_out}", 'title': ''},
                {'id': f"Amount 1 In: {amount1_in}", 'label': f"Amount 1 In: {amount1_in}", 'title': ''},
                {'id': f"Amount 1 Out: {amount1_out}", 'label': f"Amount 1 Out: {amount1_out}", 'title': ''},
                {'id': f"Amount USD: {amount_usd}", 'label': f"Amount USD: {amount_usd}", 'title': ''},
                {'id': f"Sender: {sender}", 'label': f"Sender: {sender}", 'title': ''},
                {'id': f"Receiver: {receiver}", 'label': f"Receiver: {receiver}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Swap ID: {swap_id}", 'target': f"Amount 0 In: {amount0_in}"},
                {'source': f"Swap ID: {swap_id}", 'target': f"Amount 0 Out: {amount0_out}"},
                {'source': f"Swap ID: {swap_id}", 'target': f"Amount 1 In: {amount1_in}"},
                {'source': f"Swap ID: {swap_id}", 'target': f"Amount 1 Out: {amount1_out}"},
                {'source': f"Swap ID: {swap_id}", 'target': f"Amount USD: {amount_usd}"},
                {'source': f"Swap ID: {swap_id}", 'target': f"Sender: {sender}"},
                {'source': f"Swap ID: {swap_id}", 'target': f"Receiver: {receiver}"}
            ])

        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show_buttons(filter_=['physics'])
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content
    
def create_user_network_graph():
    user_id = st.text_input("Enter user ID", "0x002525a77d262dd11ec63c9146a821b11564ce29")
    first = st.number_input("Number of liquidity positions to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["liquidityTokenBalance", "createdAtTimestamp", "reserveUSD", "volumeUSD"])
    submit_button = st.button('Submit')
    
    if submit_button:
        query = f"""
        {{
          user(id: "{user_id}") {{
            id
            liquidityPositions(
              first: {first}
              orderBy: {orderBy_options}
              orderDirection: desc
            ) {{
              id
              liquidityTokenBalance
              pair {{
                createdAtBlockNumber
                createdAtTimestamp
                name
                reserve0
                reserveETH
                reserve1
                reserveUSD
                swaps {{
                  amount0In
                  amount1In
                  amount1Out
                  amountUSD
                }}
                volumeUSD
                txCount
              }}
            }}
            usdSwapped
          }}
        }}
        """
        
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/3AMhp8Ck6ZScMibA8jfLhWFA9fKH6Zi8fMPHtb74Vsxv"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['user']['liquidityPositions'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        nodes = []
        edges = []

        user_id = data['user']['id']
        nodes.append({'id': f"User: {user_id}", 'label': f"User: {user_id}", 'title': ''})

        for position in data['user']['liquidityPositions']:
            position_id = position['id']
            liquidity_token_balance = position['liquidityTokenBalance']
            pair = position['pair']
            pair_id = pair['name']
            volume_usd = pair['volumeUSD']
            tx_count = pair['txCount']

            nodes.extend([
                {'id': f"Position ID: {position_id}", 'label': f"Position ID: {position_id}", 'title': ''},
                {'id': f"Liquidity Token Balance: {liquidity_token_balance}", 'label': f"Liquidity Token Balance: {liquidity_token_balance}", 'title': ''},
                {'id': f"Pair: {pair_id}", 'label': f"Pair: {pair_id}", 'title': ''},
                {'id': f"Volume USD: {volume_usd}", 'label': f"Volume USD: {volume_usd}", 'title': ''},
                {'id': f"Transaction Count: {tx_count}", 'label': f"Transaction Count: {tx_count}", 'title': ''}
            ])

            edges.extend([
                {'source': f"User: {user_id}", 'target': f"Position ID: {position_id}"},
                {'source': f"Position ID: {position_id}", 'target': f"Liquidity Token Balance: {liquidity_token_balance}"},
                {'source': f"Position ID: {position_id}", 'target': f"Pair: {pair_id}"},
                {'source': f"Pair: {pair_id}", 'target': f"Volume USD: {volume_usd}"},
                {'source': f"Pair: {pair_id}", 'target': f"Transaction Count: {tx_count}"}
            ])

            for swap in pair['swaps']:
                swap_amount_usd = swap['amountUSD']
                nodes.append({'id': f"Swap Amount USD: {swap_amount_usd}", 'label': f"Swap Amount USD: {swap_amount_usd}", 'title': ''})
                edges.append({'source': f"Pair: {pair_id}", 'target': f"Swap Amount USD: {swap_amount_usd}"})

        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show_buttons(filter_=['physics'])
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content



# Main function to run the Streamlit app
def swap():
    st.title('Fraxlend Explorer')
    st.markdown("### Select an Option")
    option = st.radio(
        "Select Choice",
        ("FraxswapDayDatas", "FraxswapFactories", "Tokens", "Swaps", "User"),
        index=0,
        horizontal=True
    )

    if option == 'FraxswapDayDatas':
        html_content = create_fraxswap_network_graph()
        st.components.v1.html(html_content, height=800)  
    elif option == 'FraxswapFactories':
        html_content = create_fraxswap_factories_network_graph()
        st.components.v1.html(html_content, height=800)
    elif option == 'Tokens':
        html_content = create_tokens_network_graph()
        st.components.v1.html(html_content, height=800)
    elif option == 'Swaps':
        html_content = create_swaps_network_graph()
        st.components.v1.html(html_content, height=800)
    elif option == 'User':
        html_content = create_user_network_graph()
        st.components.v1.html(html_content, height=800)
   
