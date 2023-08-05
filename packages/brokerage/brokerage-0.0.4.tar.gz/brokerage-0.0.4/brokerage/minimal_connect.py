import brokerage

# MAIN BODY OF THE PROGRAM
if __name__ == "__main__":
    username, password = "test1", "000000"  # use your own
    exchange, instrument = "BMD", "data/FCPO"  # FCPO.csv file for quote data
    exchange, instrument = "BMD", "FAKE"  # Random fake data

    conn = brokerage.login("url", username, password)  # Connect to simulator
    conn.connect(exchange, instrument)
    for d, p in conn.data_stream():
        print(d, p)

    conn.logout()  # Logout from simulator
