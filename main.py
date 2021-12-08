import pickle
from machine_learning.fraud_predictor import predict_if_btc_fraud_with_model
from graph_stuff.get_related_addresses import search_everything

# address = input("Enter the bitcoin address: ")
def get_results(btc_address):
    model_path = "models/rfc_bitcoin.bin"
    model = pickle.load(open(model_path, 'rb'))

    related_addresses = search_everything(btc_address)

    overall_fraud = False
    print("Related address explored\tIs fraud?")
    for related_address in related_addresses:
        is_fraud = predict_if_btc_fraud_with_model(related_address, model)
        print(related_address + "\t" + str(is_fraud))

        if(is_fraud == True):
            overall_fraud = True

    overall_result = "Safe" if overall_fraud == False else "Unsafe"
    print("Overall Result: " + overall_result)