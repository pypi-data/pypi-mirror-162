


## 示例

```python
L = [{"user_id": i, "algo": 0, "position": i % 5} for i in range(50)]
df = pd.DataFrame(L)


def makeReqData(json_str):
    json_str = json.loads(json_str)
    return json_str


def makeResult(r):
    data = r.get("data")
    return data



m = MultiRequest()
m.url = "http://127.0.0.1:8080/hello"
m.makeReqData = makeReqData
m.makeResult = makeResult
m.input_data = df
m.parallel_batch_size = 20
m.save_batch_size = 13
m.res_format = "fth"  # fth, csv, xlsx
m.res_dir = "data"
m.run()
```

