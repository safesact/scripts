import time
import blockcypher
# import pandas as pd
import requests as r
import json

def search_everything(search_add):
    class Graph():
        def __init__(self):
            self.edges = {}  # keys are addresses, values are list with each address in list being an edge
            self.weights = {}  # dictionary keys are tuples with (address 1, address 2), value = weight between them
            self.n = 0  # number of vertices
            self.dfs_explored = []

        def add_edge(self, add1, add2, weight):
            try:
                self.edges[add1].append(add2)
            except:
                self.edges[add1] = []
                self.edges[add1].append(add2)
                self.n += 1
            try:
                self.edges[add2].append(add1)
            except:
                self.edges[add2] = []
                self.edges[add2].append(add1)

            self.weights[(add1, add2)] = weight
            self.weights[(add2, add1)] = weight

        def DFS_Main(self, start):
            vertices = [k for k in g.edges.keys()]
            color = {}
            for v in vertices:
                color[v] = "white"
            self.DFS(start, color)
            return self.dfs_explored

        def DFS(self, v, colors):
            colors[v] = "grey"
            for w in self.edges[v]:
                if colors[w] == "white":
                    self.DFS(w, colors)
            # print(v,end=" ")
            self.dfs_explored.append(v)
            colors[v] = "black"


    def analyze_address(search_add, g, depth=1, max_depth=5, trx_limit=50):
        time.sleep(0.35)
        address_details = blockcypher.get_address_details(search_add)
        txrefs = address_details['txrefs']
        if (len(txrefs) > trx_limit):
            considered_txrefs = sorted(txrefs, key=lambda x: x["value"])[:trx_limit]
        else:
            considered_txrefs = sorted(txrefs, key=lambda x: x["value"])
        for tx in considered_txrefs:
            tx_hash = tx["tx_hash"]
            is_input = True if tx["tx_input_n"] == -1 else False
            if is_input and tx["tx_output_n"] == -1:
                print("concerning")
                break
            value = tx["value"]
            tx_details = blockcypher.get_transaction_details(tx_hash)
            if not is_input:
                receiving_add = ""
                if len(tx_details["outputs"]) == 1:  # there is no change for the transaction
                    receiving_add = tx_details["outputs"][0]["addresses"][0]
                    weight = tx_details["outputs"][0]["value"]
                else:  # there is change so we need to figure out which address is the recieving address and which is change
                    if tx_details["outputs"][0]["value"] > tx_details["outputs"][1]["value"]:
                        receiving_add = tx_details["outputs"][0]["addresses"][0]
                        weight = tx_details["outputs"][0]["value"]
                    else:
                        receiving_add = tx_details["outputs"][1]["addresses"][0]
                        weight = tx_details["outputs"][1]["value"]
                if receiving_add not in g.edges.keys():
                    g.add_edge(search_add, receiving_add, value)
                    if depth < max_depth:
                        g = analyze_address(receiving_add, g, depth=depth + 1)

            else:  # its an input to search address

                for inp in tx_details["inputs"]:
                    output_add = inp["addresses"][0]
                    value = inp["output_value"]
                    if output_add not in g.edges.keys():
                        g.add_edge(output_add, search_add, value)
                        if depth < max_depth:
                            g = analyze_address(output_add, g, depth=depth + 1)

        return g

    # search_add = "111K8kZAEnJg245r2cM6y9zgJGHZtJPy6"
    # address_details = blockcypher.get_address_details(search_add)

    g = Graph()
    g = analyze_address(search_add, g, max_depth=1)
    return g.DFS_Main(search_add)