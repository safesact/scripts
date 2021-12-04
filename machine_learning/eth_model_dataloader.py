import requests
from datetime import datetime

'''
Needed:
['Avg min between sent tnx',
 'Avg min between received tnx',
 'Time Diff between first and last (Mins)',
 'Sent tnx',
 'Received Tnx',
 'Unique Received From Addresses',
 'Unique Sent To Addresses',
 'min value received',
 'max value received ',
 'avg val received',
 'min val sent',
 'max val sent',
 'avg val sent',
 'total Ether sent',
 'total ether received',
 'total ether balance']
'''

# The main function to be invoked for providing data to the model
def get_account_summary(account_address, convert_to_eth=True):
    blockchain_info_response = requests.get("https://blockchain.info/rawaddr/" + account_address)

    response_status_code = blockchain_info_response.status_code

    if response_status_code != 200:
        print("Got to an error: " + str(blockchain_info_response))
        if response_status_code == 429:
            raise Exception("The API does not allow you to make too many requests")
        else:
            raise Exception("The requested Bitcoin address does not exist")

    full_account_details = blockchain_info_response.json()

    avg_time_bw_sent_trxs, avg_time_bw_rec_trxs = calculate_average_time_between_transactions(
        full_account_details["txs"])
    td_bw_fandl_trxs = calculate_time_between_first_and_last_transactions(full_account_details["txs"])
    n_sent, n_received, unique_received_from_addresses, unique_sent_to_addresses, min_received, max_received, avg_received, min_sent, max_sent, avg_sent = get_transaction_stats(
        full_account_details["txs"])
    # print((n_sent, n_received, unique_received_from_addresses, unique_sent_to_addresses, min_received, max_received, avg_received, min_sent, max_sent, avg_sent))
    total_sent = full_account_details["total_sent"]
    total_received = full_account_details["total_received"]
    total_balance = full_account_details["final_balance"]

    div = 100000000

    if convert_to_eth == True:
        ret_data = [
            avg_time_bw_sent_trxs,
            avg_time_bw_rec_trxs,
            td_bw_fandl_trxs,
            n_sent,
            n_received,
            unique_received_from_addresses,
            unique_sent_to_addresses,
            get_value_in_eth(min_received / div),
            get_value_in_eth(max_received / div),
            get_value_in_eth(avg_received / div),
            get_value_in_eth(min_sent / div),
            get_value_in_eth(max_sent / div),
            get_value_in_eth(avg_sent / div),
            get_value_in_eth(total_sent / div),
            get_value_in_eth(total_received / div),
            get_value_in_eth(total_balance / div),
        ]

    else:
        ret_data = [
            avg_time_bw_sent_trxs,
            avg_time_bw_rec_trxs,
            td_bw_fandl_trxs,
            n_sent,
            n_received,
            unique_received_from_addresses,
            unique_sent_to_addresses,
            min_received / div,
            max_received / div,
            avg_received / div,
            min_sent / div,
            max_sent / div,
            avg_sent / div,
            total_sent / div,
            total_received / div,
            total_balance / div,
        ]

    return ret_data


# More helpers
def calculate_time_between_first_and_last_transactions(transactions):
    if (len(transactions) < 0):
        return 0

    last_trx_dt = datetime.fromtimestamp(transactions[0]["time"])
    first_trx_dt = datetime.fromtimestamp(transactions[-1]["time"])

    time_diff = (last_trx_dt - first_trx_dt).total_seconds()

    return time_diff / 60


def get_transaction_stats(transactions):
    unique_sent_to_addresses = set()
    n_sent = 0
    min_sent = float('inf')
    max_sent = -float('inf')
    total_sent = 0
    avg_sent = 0

    unique_received_from_addresses = set()
    n_received = 0
    min_received = float('inf')
    max_received = -float('inf')
    total_received = 0
    avg_received = 0

    for transaction in transactions:
        if (transaction["result"] < 0):
            n_sent += 1
            for sender in transaction["out"]:
                unique_sent_to_addresses.add(sender["addr"])

            amt = - transaction["result"]
            total_sent += amt
            min_sent = min(min_sent, amt)
            max_sent = max(max_sent, amt)

        else:
            n_received += 1
            for receiver in transaction["out"]:
                unique_received_from_addresses.add(receiver["addr"])

            amt = transaction["result"]
            total_received += amt
            min_received = min(min_sent, amt)
            max_received = max(max_sent, amt)

    min_received = 0 if min_received == float('inf') else min_received
    max_received = 0 if max_received == -float('inf') else max_received
    avg_received = total_received / n_received if n_received > 0 else 0

    min_sent = 0 if min_sent == float('inf') else min_sent
    max_sent = 0 if max_sent == -float('inf') else max_sent
    avg_sent = total_sent / n_sent if n_sent > 0 else 0

    return n_sent, n_received, len(unique_received_from_addresses), len(
        unique_sent_to_addresses), min_received, max_received, avg_received, min_sent, max_sent, avg_sent


def calculate_average_time_between_transactions(transactions):
    if (len(transactions) < 2):
        return 0, 0
    else:
        # For sent transactions
        n_diff_count_for_sent = 0
        total_diffs_for_sent = 0
        prev_sent_trx_for_sent = None

        n_diff_count_for_received = 0
        total_diffs_for_received = 0
        prev_sent_trx_for_received = None

        for trx in transactions:
            if (trx["result"] < 0):
                if prev_sent_trx_for_sent == None:
                    prev_sent_trx_for_sent = trx
                    continue
                else:
                    t2_time = datetime.fromtimestamp(prev_sent_trx_for_sent["time"])
                    t1_time = datetime.fromtimestamp(trx["time"])
                    n_diff_count_for_sent += 1
                    total_diffs_for_sent += (t2_time - t1_time).total_seconds()
                    prev_sent_trx_for_sent = trx

            else:
                if prev_sent_trx_for_received == None:
                    prev_sent_trx_for_received = trx
                    continue
                else:
                    t2_time = datetime.fromtimestamp(prev_sent_trx_for_received["time"])
                    t1_time = datetime.fromtimestamp(trx["time"])
                    n_diff_count_for_received += 1
                    total_diffs_for_received += (t2_time - t1_time).total_seconds()
                    prev_sent_trx_for_received = trx

        avg_bw_sent_mins = (total_diffs_for_sent / n_diff_count_for_sent) / 60 if n_diff_count_for_sent != 0 else 0
        avg_bw_received_mins = (
                                           total_diffs_for_received / n_diff_count_for_received) / 60 if n_diff_count_for_received != 0 else 0

        return avg_bw_sent_mins, avg_bw_received_mins

def get_value_in_eth(value_in_btc, conversion_rate = 13.69):
    return value_in_btc * conversion_rate