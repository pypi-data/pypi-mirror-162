from pyperspace import Daemon, DataSetConfig, StorageConfig
from pyperspace.data import Entry
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class DataEntry(BaseModel):
    time: int
    data: bytes

def generate_api(data_dir: str) -> FastAPI:
    app = FastAPI(title="Pyperspace Frontend", version="0.1.1", docs_url="/")
    db = Daemon(data_dir, DataSetConfig(), StorageConfig(cycle_time=60))

    @app.on_event("startup")
    async def startup():
        db.start()

    @app.on_event("shutdown")
    async def shutdown():
        db.stop()
        db.close()

    @app.post("/api/v1/dataset/{name}/create")
    async def create_dataset(name: str):
        db.send_create(name)
        return {"success": True}

    @app.post("/api/v1/dataset/{name}/drop")
    async def drop_dataset(name: str):
        db.send_drop(name)
        return {"success": True}

    @app.get("/api/v1/datasets")
    async def list_datasets():
        return {"success": True, "datasets": list(db.datasets)}
    
    @app.get("/api/v1/dataset/{name}/stats")
    async def get_dataset_stats(name: str):
        ds = db.open_lsm_dataset(name)
        try:
            begin_time, end_time, num_entries = ds.stats
            return {"success": True, "dataset": name, "begin_time": begin_time, "end_time": end_time, "num_entries": num_entries}
        finally:
            ds.close()

    @app.post("/api/v1/dataset/{name}/insert")
    async def insert_rows(name: str, rows: List[DataEntry]):
        db.send_insert_many(name, (Entry(e.time, e.data) for e in rows))
        return {"success": True}

    @app.post("/api/v1/dataset/{name}/delete")
    async def delete_range(name: str, begin: int, end: int):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.delete(begin, end)
        finally:
            ds.close()
        return {"success": True}

    @app.get("/api/v1/dataset/{name}/select")
    async def select_range(name: str, begin: int, end: int):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.find_range(begin, end)
            return {"success": True, "data": [{"time": e.time, "data": e.data.tobytes()} for e in data]}
        finally:
            ds.close()

    @app.get("/api/v1/dataset/{name}/select-all")
    async def select_all(name: str):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.find_all()
            return {"success": True, "data": [{"time": e.time, "data": e.data.tobytes()} for e in data]}
        finally:
            ds.close()

    return app
