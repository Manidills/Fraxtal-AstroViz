from io import StringIO
import streamlit as st
import pandas as pd
import requests
import json
from pyvis.network import Network
import tempfile


def create_bridge_actions_network_graph():
    # User input for the query parameters
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["amount"])
    submit_button = st.button('Submit')
    
    if submit_button:
        # Constructing the query with user input
        query = f"""
        {{
          bridgeActions(first: {first}, orderBy: {orderBy_options}, orderDirection: desc) {{
            id
            fromAddress {{
              id
              address
              chain
            }}
            toAddress {{
              id
              address
              chain
            }}
            fromChain
            amount
            block
            toChain
            timestamp
          }}
        }}
        """
        
        # Updated URL for the GraphQL endpoint
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/HTkQvHkKroPxygp8B2yrwSrRe1MMzvSpvUmXoPypfXAw"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['bridgeActions'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        # Extracting data for nodes and edges
        nodes = []
        edges = []
        
        for action in data['bridgeActions']:
            from_address = action['fromAddress']['address']
            to_address = action['toAddress']['address']
            amount = action['amount']
            from_chain = action['fromChain']
            to_chain = action['toChain']
            timestamp = action['timestamp']
            block = action['block']
            
            # Adding nodes
            nodes.extend([
                {'id': f"From: {from_address}", 'label': f"From: {from_address}", 'title': f"Chain: {from_chain}"},
                {'id': f"To: {to_address}", 'label': f"To: {to_address}", 'title': f"Chain: {to_chain}"},
                {'id': f"Amount: {amount}", 'label': f"Amount: {amount}", 'title': f"Timestamp: {timestamp}"},
                {'id': f"Block: {block}", 'label': f"Block: {block}", 'title': ''}
            ])
            
            # Adding edges
            edges.extend([
                {'source': f"From: {from_address}", 'target': f"To: {to_address}"},
                {'source': f"To: {to_address}", 'target': f"Amount: {amount}"},
                {'source': f"Amount: {amount}", 'target': f"Block: {block}"}
            ])
        
        # Creating the network graph
        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        # Using a temporary file to display the graph
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content

def create_tokens_network_graph():
    # User input for the query parameters
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["totalSupply"])
    submit_button = st.button('Submit')
    
    if submit_button:
        # Constructing the query with user input
        query = f"""
        {{
          tokens(first: {first}, orderBy: {orderBy_options}, orderDirection: desc) {{
            id
            chain
            address
            decimals
            name
            symbol
            totalSupply
          }}
        }}
        """
        
        # Updated URL for the GraphQL endpoint
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/HTkQvHkKroPxygp8B2yrwSrRe1MMzvSpvUmXoPypfXAw"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['tokens'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        # Extracting data for nodes and edges
        nodes = []
        edges = []
        
        for token in data['tokens']:
            token_id = token['id']
            chain = token['chain']
            address = token['address']
            decimals = token['decimals']
            name = token['name']
            symbol = token['symbol']
            totalSupply = token['totalSupply']
            
            # Adding nodes
            nodes.extend([
                {'id': f"Token ID: {token_id}", 'label': f"Token ID: {token_id}", 'title': ''},
                {'id': f"Name: {name}", 'label': f"Name: {name}", 'title': ''},
                {'id': f"Symbol: {symbol}", 'label': f"Symbol: {symbol}", 'title': ''},
                {'id': f"Total Supply: {totalSupply}", 'label': f"Total Supply: {totalSupply}", 'title': ''},
                {'id': f"Chain: {chain}", 'label': f"Chain: {chain}", 'title': ''},
                {'id': f"Address: {address}", 'label': f"Address: {address}", 'title': ''},
                {'id': f"Decimals: {decimals}", 'label': f"Decimals: {decimals}", 'title': ''}
            ])
            
            # Adding edges
            edges.extend([
                {'source': f"Token ID: {token_id}", 'target': f"Name: {name}"},
                {'source': f"Token ID: {token_id}", 'target': f"Symbol: {symbol}"},
                {'source': f"Token ID: {token_id}", 'target': f"Total Supply: {totalSupply}"},
                {'source': f"Token ID: {token_id}", 'target': f"Chain: {chain}"},
                {'source': f"Token ID: {token_id}", 'target': f"Address: {address}"},
                {'source': f"Token ID: {token_id}", 'target': f"Decimals: {decimals}"}
            ])
        
        # Creating the network graph
        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        # Using a temporary file to display the graph
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content


def create_users_network_graph():
    # User inputs for the query parameters
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy = st.selectbox("Order By", ["chain", "id", "address"])
    orderDirection = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')
    
    if submit_button:
        # Constructing the query with user input
        query = f"""
        {{
          users(first: {first}, orderBy: {orderBy}, orderDirection: {orderDirection}) {{
            address
            chain
            id
            toBridgeActions(first: 10, orderBy: amount) {{
              fromChain
              id
              timestamp
              toChain
              tokenOnToChain {{
                address
                chain
                decimals
                totalSupply
              }}
              tokenOnFromChain {{
                address
                chain
                totalSupply
                symbol
                name
              }}
              amount
            }}
          }}
        }}
        """
        
        # Updated URL for the GraphQL endpoint
        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/HTkQvHkKroPxygp8B2yrwSrRe1MMzvSpvUmXoPypfXAw"
        response = requests.post(url, json={'query': query})
        
        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['users'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")
        
        # Extracting data for nodes and edges
        nodes = []
        edges = []
        
        for user in data['users']:
            user_id = user['id']
            user_address = user['address']
            user_chain = user['chain']
            
            nodes.append({'id': f"User ID: {user_id}", 'label': f"User ID: {user_id}", 'title': f"Address: {user_address}, Chain: {user_chain}"})
            
            for action in user['toBridgeActions']:
                action_id = action['id']
                from_chain = action['fromChain']
                to_chain = action['toChain']
                timestamp = action['timestamp']
                amount = action['amount']
                token_to_chain = action['tokenOnToChain']
                token_from_chain = action['tokenOnFromChain']
                
                nodes.extend([
                    {'id': f"Action ID: {action_id}", 'label': f"Action ID: {action_id}", 'title': f"From Chain: {from_chain}, To Chain: {to_chain}, Amount: {amount}"},
                    {'id': f"Token To Chain: {token_to_chain['address']}", 'label': f"Token To Chain: {token_to_chain['address']}", 'title': f"Chain: {token_to_chain['chain']}, Total Supply: {token_to_chain['totalSupply']}, Decimals: {token_to_chain['decimals']}"},
                    {'id': f"Token From Chain: {token_from_chain['address']}", 'label': f"Token From Chain: {token_from_chain['address']}", 'title': f"Chain: {token_from_chain['chain']}, Total Supply: {token_from_chain['totalSupply']}, Symbol: {token_from_chain['symbol']}, Name: {token_from_chain['name']}"}
                ])
                
                edges.extend([
                    {'source': f"User ID: {user_id}", 'target': f"Action ID: {action_id}"},
                    {'source': f"Action ID: {action_id}", 'target': f"Token To Chain: {token_to_chain['address']}"},
                    {'source': f"Action ID: {action_id}", 'target': f"Token From Chain: {token_from_chain['address']}"}
                ])
        
        # Creating the network graph
        graph = Network(height="800px", width="100%", notebook=True)
        
        for node in nodes:
            graph.add_node(node['id'], label=node['label'], title=node['title'])
        
        for edge in edges:
            graph.add_edge(edge['source'], edge['target'])

        # Using a temporary file to display the graph
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            graph.show(tmpfile.name)
            tmpfile.seek(0)
            html_content = tmpfile.read().decode("utf-8")

        return html_content







def Bridge():
    st.title('FraxBridging Explorer')
    st.markdown("### Select an Option")
    option = st.radio(
        "Select Choice",
        ("BridgeActions", "Tokens", "Users"),
        index=0,
        horizontal=True
    )

    if option == 'BridgeActions':
        html_content = create_bridge_actions_network_graph()
        st.components.v1.html(html_content, height=800)
    elif option == 'Tokens':
        html_content = create_tokens_network_graph()
        st.components.v1.html(html_content, height=800) 
    elif option == 'Users':
        html_content = create_users_network_graph()
        st.components.v1.html(html_content, height=800)
    
