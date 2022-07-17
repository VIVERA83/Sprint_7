from uuid import uuid4

data = uuid4().hex[:10]
role = {"name": f"test_{data}"}
