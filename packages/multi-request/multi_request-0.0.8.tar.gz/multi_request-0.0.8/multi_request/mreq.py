import os
import concurrent.futures
import requests
import pandas as pd


class MultiRequest:
    def __init__(self,
                 url=None,
                 input_data=None,
                 makeReqData=None,
                 makeResult=None,
                 res_dir="data",
                 parallel_batch_size=100,
                 save_batch_size=5000,
                 res_format="fth"):
        self.url = url
        self.makeReqData = makeReqData
        self.makeResult = makeResult
        self.res_dir = res_dir
        self.input_data = input_data
        self.parallel_batch_size = parallel_batch_size
        self.save_batch_size = save_batch_size
        self.res_format = res_format


    def call_service(self, reqData):
        response = requests.post(self.url, json=reqData)
        result = response.json()
        if self.makeResult is not None:
            result = self.makeResult(result)
        return result


    def save_result(self, batch, start_num, end_num):
        if not os.path.exists(self.res_dir):
            os.makedirs(self.res_dir, exist_ok=True)
        filepath = ""
        if self.res_format == "fth":
            filepath = os.path.join(self.res_dir, f"{start_num}_{end_num}.fth")
            pd.DataFrame(batch).to_feather(filepath)
        elif self.res_format == "csv":
            filepath = os.path.join(self.res_dir, f"{start_num}_{end_num}.csv")
            pd.DataFrame(batch).to_csv(filepath)
        elif self.res_format == "xlsx":
            filepath = os.path.join(self.res_dir, f"{start_num}_{end_num}.xlsx")
            pd.DataFrame(batch).to_excel(filepath)
        else:
            pass
        print(f"saved: {filepath}")

    def consumer(self, save_batch_size=10):
        batch = []
        start_num = 0
        end_num = 0
        while True:
            result = yield
            if not result:
                continue
            if result == "finish":
                start_num = end_num
                end_num = start_num + len(batch)
                if len(batch) > 0:
                    self.save_result(batch, start_num, end_num)
                return
            batch.append(result)
            if len(batch) >= save_batch_size:
                start_num = end_num
                end_num += len(batch)
                self.save_result(batch, start_num, end_num)
                batch = []

    def run(self):
        c = self.consumer(save_batch_size=self.save_batch_size)
        c.send(None)
        df = self.input_data
        n = self.parallel_batch_size
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(df.shape[0] // n + 1):
                print(f"{i * n}:{(i + 1) * n}")
                reqDataList = [self.makeReqData(row.to_json()) for _, row in df.iloc[i * n:(i + 1) * n].iterrows()]
                for result in executor.map(self.call_service, reqDataList):
                    c.send(result)
            try:
                c.send("finish")
            except StopIteration:
                print("ALL TASK DONE.")
                return

