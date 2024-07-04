from io import StringIO
import streamlit as st
import pandas as pd
import requests
import json
from pyvis.network import Network
import tempfile


def create_pools_network_graph():
    first = st.number_input("Number of pools to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["totalValueLockedUSD", "stakedOutputTokenAmount", "cumulativeTotalRevenueUSD"])
    orderDirection_options = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = f"""
        {{
          pools(first: {first}, orderBy: {orderBy_options}, orderDirection: {orderDirection_options}) {{
            createdBlockNumber
            createdTimestamp
            cumulativeProtocolSideRevenueUSD
            cumulativeSupplySideRevenueUSD
            cumulativeTotalRevenueUSD
            id
            inputTokenBalances
            inputTokenBalancesUSD
            isLiquidityToken
            lastSnapshotDayID
            stakedOutputTokenAmount
            rewardTokenEmissionsUSD
            rewardTokenEmissionsAmount
            outputTokenPriceUSD
            outputTokenSupply
            totalValueLockedUSD
            symbol
          }}
        }}
        """

        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/FeKHrGeNxVctN6EeAhba2Kv78xNxuEhbRKNECLfVH8z2"
        response = requests.post(url, json={'query': query})

        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['pools'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

        nodes = []
        edges = []

        for pool in data['pools']:
            pool_id = pool['id']
            total_value_locked_usd = pool['totalValueLockedUSD']
            created_timestamp = pool['createdTimestamp']
            cumulative_total_revenue_usd = pool['cumulativeTotalRevenueUSD']
            input_token_balances = pool['inputTokenBalances']
            input_token_balances_usd = pool['inputTokenBalancesUSD']
            symbol = pool['symbol']

            nodes.extend([
                {'id': f"Pool ID: {pool_id}", 'label': f"Pool ID: {pool_id}", 'title': ''},
                {'id': f"Total Value Locked USD: {total_value_locked_usd}", 'label': f"Total Value Locked USD: {total_value_locked_usd}", 'title': ''},
                {'id': f"Created Timestamp: {created_timestamp}", 'label': f"Created Timestamp: {created_timestamp}", 'title': ''},
                {'id': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}", 'label': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}", 'title': ''},
                {'id': f"Input Token Balances: {input_token_balances}", 'label': f"Input Token Balances: {input_token_balances}", 'title': ''},
                {'id': f"Input Token Balances USD: {input_token_balances_usd}", 'label': f"Input Token Balances USD: {input_token_balances_usd}", 'title': ''},
                {'id': f"Symbol: {symbol}", 'label': f"Symbol: {symbol}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Pool ID: {pool_id}", 'target': f"Total Value Locked USD: {total_value_locked_usd}"},
                {'source': f"Pool ID: {pool_id}", 'target': f"Created Timestamp: {created_timestamp}"},
                {'source': f"Pool ID: {pool_id}", 'target': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}"},
                {'source': f"Pool ID: {pool_id}", 'target': f"Input Token Balances: {input_token_balances}"},
                {'source': f"Pool ID: {pool_id}", 'target': f"Input Token Balances USD: {input_token_balances_usd}"},
                {'source': f"Pool ID: {pool_id}", 'target': f"Symbol: {symbol}"}
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
    

def create_pool_daily_snapshots_network_graph():
    first = st.number_input("Number of snapshots to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["totalValueLockedUSD", "cumulativeTotalRevenueUSD", "dailyTotalRevenueUSD"])
    orderDirection_options = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = f"""
        {{
          poolDailySnapshots(first: {first}, orderBy: {orderBy_options}, orderDirection: {orderDirection_options}) {{
            blockNumber
            cumulativeProtocolSideRevenueUSD
            cumulativeSupplySideRevenueUSD
            cumulativeTotalRevenueUSD
            dailyProtocolSideRevenueUSD
            dailySupplySideRevenueUSD
            dailyTotalRevenueUSD
            day
            id
            inputTokenBalances
            inputTokenBalancesUSD
            outputTokenPriceUSD
            outputTokenSupply
            rewardTokenEmissionsAmount
            rewardTokenEmissionsUSD
            stakedOutputTokenAmount
            timestamp
            totalValueLockedUSD
            pool {{
              totalValueLockedUSD
              stakedOutputTokenAmount
              name
              outputTokenPriceUSD
              outputTokenSupply
            }}
          }}
        }}
        """

        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/FeKHrGeNxVctN6EeAhba2Kv78xNxuEhbRKNECLfVH8z2"
        response = requests.post(url, json={'query': query})

        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['poolDailySnapshots'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

        nodes = []
        edges = []

        for snapshot in data['poolDailySnapshots']:
            snapshot_id = snapshot['id']
            block_number = snapshot['blockNumber']
            cumulative_total_revenue_usd = snapshot['cumulativeTotalRevenueUSD']
            daily_total_revenue_usd = snapshot['dailyTotalRevenueUSD']
            total_value_locked_usd = snapshot['totalValueLockedUSD']
            timestamp = snapshot['timestamp']
            pool_name = snapshot['pool']['name']

            nodes.extend([
                {'id': f"Snapshot ID: {snapshot_id}", 'label': f"Snapshot ID: {snapshot_id}", 'title': ''},
                {'id': f"Block Number: {block_number}", 'label': f"Block Number: {block_number}", 'title': ''},
                {'id': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}", 'label': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}", 'title': ''},
                {'id': f"Daily Total Revenue USD: {daily_total_revenue_usd}", 'label': f"Daily Total Revenue USD: {daily_total_revenue_usd}", 'title': ''},
                {'id': f"Total Value Locked USD: {total_value_locked_usd}", 'label': f"Total Value Locked USD: {total_value_locked_usd}", 'title': ''},
                {'id': f"Timestamp: {timestamp}", 'label': f"Timestamp: {timestamp}", 'title': ''},
                {'id': f"Pool Name: {pool_name}", 'label': f"Pool Name: {pool_name}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Block Number: {block_number}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Daily Total Revenue USD: {daily_total_revenue_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Total Value Locked USD: {total_value_locked_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Timestamp: {timestamp}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Pool Name: {pool_name}"}
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
    
def create_financials_daily_snapshots_network_graph():
    first = st.number_input("Number of snapshots to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["cumulativeTotalRevenueUSD", "totalValueLockedUSD", "dailyTotalRevenueUSD"])
    orderDirection_options = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = f"""
        {{
          financialsDailySnapshots(first: {first}, orderBy: {orderBy_options}, orderDirection: {orderDirection_options}) {{
            cumulativeProtocolSideRevenueUSD
            cumulativeSupplySideRevenueUSD
            cumulativeTotalRevenueUSD
            dailyProtocolSideRevenueUSD
            dailySupplySideRevenueUSD
            dailyTotalRevenueUSD
            day
            protocolControlledValueUSD
            timestamp
            totalValueLockedUSD
            blockNumber
            id
            protocol {{
              totalPoolCount
              totalValueLockedUSD
              lastSnapshotDayID
              lastSnapshotHourID
              cumulativeTotalRevenueUSD
              cumulativeTransactionCount
            }}
          }}
        }}
        """

        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/FeKHrGeNxVctN6EeAhba2Kv78xNxuEhbRKNECLfVH8z2"
        response = requests.post(url, json={'query': query})

        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['financialsDailySnapshots'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

        nodes = []
        edges = []

        for snapshot in data['financialsDailySnapshots']:
            snapshot_id = snapshot['id']
            cumulative_total_revenue_usd = snapshot['cumulativeTotalRevenueUSD']
            daily_total_revenue_usd = snapshot['dailyTotalRevenueUSD']
            total_value_locked_usd = snapshot['totalValueLockedUSD']
            timestamp = snapshot['timestamp']
            protocol_id = snapshot['protocol']['totalPoolCount']
            protocol_total_value_locked_usd = snapshot['protocol']['totalValueLockedUSD']
            protocol_cumulative_total_revenue_usd = snapshot['protocol']['cumulativeTotalRevenueUSD']
            protocol_transaction_count = snapshot['protocol']['cumulativeTransactionCount']

            nodes.extend([
                {'id': f"Snapshot ID: {snapshot_id}", 'label': f"Snapshot ID: {snapshot_id}", 'title': ''},
                {'id': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}", 'label': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}", 'title': ''},
                {'id': f"Daily Total Revenue USD: {daily_total_revenue_usd}", 'label': f"Daily Total Revenue USD: {daily_total_revenue_usd}", 'title': ''},
                {'id': f"Total Value Locked USD: {total_value_locked_usd}", 'label': f"Total Value Locked USD: {total_value_locked_usd}", 'title': ''},
                {'id': f"Timestamp: {timestamp}", 'label': f"Timestamp: {timestamp}", 'title': ''},
                {'id': f"Protocol Pool Count: {protocol_id}", 'label': f"Protocol Pool Count: {protocol_id}", 'title': ''},
                {'id': f"Protocol Total Value Locked USD: {protocol_total_value_locked_usd}", 'label': f"Protocol Total Value Locked USD: {protocol_total_value_locked_usd}", 'title': ''},
                {'id': f"Protocol Cumulative Total Revenue USD: {protocol_cumulative_total_revenue_usd}", 'label': f"Protocol Cumulative Total Revenue USD: {protocol_cumulative_total_revenue_usd}", 'title': ''},
                {'id': f"Protocol Transaction Count: {protocol_transaction_count}", 'label': f"Protocol Transaction Count: {protocol_transaction_count}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Cumulative Total Revenue USD: {cumulative_total_revenue_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Daily Total Revenue USD: {daily_total_revenue_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Total Value Locked USD: {total_value_locked_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Timestamp: {timestamp}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Pool Count: {protocol_id}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Total Value Locked USD: {protocol_total_value_locked_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Cumulative Total Revenue USD: {protocol_cumulative_total_revenue_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Transaction Count: {protocol_transaction_count}"}
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
    
def create_network_graph():
    first = st.number_input("Number of records to fetch", min_value=1, max_value=50, value=10)
    orderBy_options = st.selectbox("Order By", ["dailyActiveUsers", "cumulativeTransactionCount", "dailyTransactionCount"])
    orderDirection_options = st.selectbox("Order Direction", ["asc", "desc"])
    submit_button = st.button('Submit')

    if submit_button:
        query = f"""
        {{
          usageMetricsDailySnapshots(first: {first}, orderBy: {orderBy_options}, orderDirection: {orderDirection_options}) {{
            blockNumber
            cumulativeTransactionCount
            cumulativeUniqueUsers
            dailyActiveUsers
            dailyTransactionCount
            day
            id
            timestamp
            totalPoolCount
            protocol {{
              cumulativeTotalRevenueUSD
              cumulativeTransactionCount
              cumulativeUniqueUsers
              totalValueLockedUSD
              totalPoolCount
              network
              lastSnapshotDayID
              lastSnapshotHourID
            }}
          }}
        }}
        """

        url = "https://gateway-arbitrum.network.thegraph.com/api/535e83a86f270e66f83c6227ae349334/subgraphs/id/FeKHrGeNxVctN6EeAhba2Kv78xNxuEhbRKNECLfVH8z2"
        response = requests.post(url, json={'query': query})

        if response.status_code == 200:
            data = response.json()['data']
            st.dataframe(data['usageMetricsDailySnapshots'])
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

        nodes = []
        edges = []

        for snapshot in data['usageMetricsDailySnapshots']:
            snapshot_id = snapshot['id']
            block_number = snapshot['blockNumber']
            cumulative_transaction_count = snapshot['cumulativeTransactionCount']
            cumulative_unique_users = snapshot['cumulativeUniqueUsers']
            daily_active_users = snapshot['dailyActiveUsers']
            daily_transaction_count = snapshot['dailyTransactionCount']
            day = snapshot['day']
            timestamp = snapshot['timestamp']
            total_pool_count = snapshot['totalPoolCount']
            protocol = snapshot['protocol']
            protocol_revenue_usd = protocol['cumulativeTotalRevenueUSD']
            protocol_transaction_count = protocol['cumulativeTransactionCount']
            protocol_unique_users = protocol['cumulativeUniqueUsers']
            protocol_value_locked_usd = protocol['totalValueLockedUSD']
            protocol_pool_count = protocol['totalPoolCount']
            protocol_network = protocol['network']
            protocol_last_snapshot_day_id = protocol['lastSnapshotDayID']
            protocol_last_snapshot_hour_id = protocol['lastSnapshotHourID']

            nodes.extend([
                {'id': f"Snapshot ID: {snapshot_id}", 'label': f"Snapshot ID: {snapshot_id}", 'title': ''},
                {'id': f"Block Number: {block_number}", 'label': f"Block Number: {block_number}", 'title': ''},
                {'id': f"Cumulative Transaction Count: {cumulative_transaction_count}", 'label': f"Cumulative Transaction Count: {cumulative_transaction_count}", 'title': ''},
                {'id': f"Cumulative Unique Users: {cumulative_unique_users}", 'label': f"Cumulative Unique Users: {cumulative_unique_users}", 'title': ''},
                {'id': f"Daily Active Users: {daily_active_users}", 'label': f"Daily Active Users: {daily_active_users}", 'title': ''},
                {'id': f"Daily Transaction Count: {daily_transaction_count}", 'label': f"Daily Transaction Count: {daily_transaction_count}", 'title': ''},
                {'id': f"Day: {day}", 'label': f"Day: {day}", 'title': ''},
                {'id': f"Timestamp: {timestamp}", 'label': f"Timestamp: {timestamp}", 'title': ''},
                {'id': f"Total Pool Count: {total_pool_count}", 'label': f"Total Pool Count: {total_pool_count}", 'title': ''},
                {'id': f"Protocol Revenue USD: {protocol_revenue_usd}", 'label': f"Protocol Revenue USD: {protocol_revenue_usd}", 'title': ''},
                {'id': f"Protocol Transaction Count: {protocol_transaction_count}", 'label': f"Protocol Transaction Count: {protocol_transaction_count}", 'title': ''},
                {'id': f"Protocol Unique Users: {protocol_unique_users}", 'label': f"Protocol Unique Users: {protocol_unique_users}", 'title': ''},
                {'id': f"Protocol Value Locked USD: {protocol_value_locked_usd}", 'label': f"Protocol Value Locked USD: {protocol_value_locked_usd}", 'title': ''},
                {'id': f"Protocol Pool Count: {protocol_pool_count}", 'label': f"Protocol Pool Count: {protocol_pool_count}", 'title': ''},
                {'id': f"Protocol Network: {protocol_network}", 'label': f"Protocol Network: {protocol_network}", 'title': ''},
                {'id': f"Protocol Last Snapshot Day ID: {protocol_last_snapshot_day_id}", 'label': f"Protocol Last Snapshot Day ID: {protocol_last_snapshot_day_id}", 'title': ''},
                {'id': f"Protocol Last Snapshot Hour ID: {protocol_last_snapshot_hour_id}", 'label': f"Protocol Last Snapshot Hour ID: {protocol_last_snapshot_hour_id}", 'title': ''}
            ])

            edges.extend([
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Block Number: {block_number}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Cumulative Transaction Count: {cumulative_transaction_count}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Cumulative Unique Users: {cumulative_unique_users}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Daily Active Users: {daily_active_users}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Daily Transaction Count: {daily_transaction_count}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Day: {day}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Timestamp: {timestamp}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Total Pool Count: {total_pool_count}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Revenue USD: {protocol_revenue_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Transaction Count: {protocol_transaction_count}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Unique Users: {protocol_unique_users}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Value Locked USD: {protocol_value_locked_usd}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Pool Count: {protocol_pool_count}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Network: {protocol_network}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Last Snapshot Day ID: {protocol_last_snapshot_day_id}"},
                {'source': f"Snapshot ID: {snapshot_id}", 'target': f"Protocol Last Snapshot Hour ID: {protocol_last_snapshot_hour_id}"}
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

def staking():
    st.title('FraxEthStaking Explorer')
    st.markdown("### Select an Option")
    option = st.radio(
        "Select Choice",
        ("Pools", "PoolDailySnapshots", "FinancialsDailySnapshots", "UsageMetricsDailySnapshots"),
        index=0,
        horizontal=True
    )

    if option == 'Pools':
        html_content = create_pools_network_graph()
        st.components.v1.html(html_content, height=800) 
    elif option == 'PoolDailySnapshots':
        html_content = create_pool_daily_snapshots_network_graph()
        st.components.v1.html(html_content, height=800)
    elif option == 'FinancialsDailySnapshots':
        html_content = create_financials_daily_snapshots_network_graph()
        st.components.v1.html(html_content, height=800)
    elif option == 'UsageMetricsDailySnapshots':
        html_content = create_network_graph()
        st.components.v1.html(html_content, height=800)