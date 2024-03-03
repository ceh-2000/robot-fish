import requests
import pandas as pd
import time

def cur_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)

if __name__=="__main__":
    path_to_data = f"data-{cur_time()}.csv"
    df = pd.DataFrame(columns=["Time", "Light"])
    elapsed_time = 0 # Use this to save every ten seconds

    while True:
        response = requests.get("http://172.20.10.12:5000/get-light")
        data = float(response.text.split(" ")[0])

        new_data = {"Time": cur_time(), "Light": data}
        print(new_data)
        df = df._append(new_data, ignore_index=True)

        if elapsed_time == 10:
            df.to_csv(path_to_data, index=False)
            elapsed_time = 0

        elapsed_time += 1
        time.sleep(1)