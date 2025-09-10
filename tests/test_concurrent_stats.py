import asyncio
import os
import sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

settings_path = os.path.join(ROOT, "settings.json")
if not os.path.exists(settings_path):
    with open(settings_path, "w") as fp:
        fp.write("{}")

import function as func

class DummyCollection:
    def __init__(self):
        self.store = {}

    async def update_one(self, filter, update):
        doc = self.store.setdefault(filter["_id"], {})
        for op, action in update.items():
            if op == "$inc":
                for k, v in action.items():
                    doc[k] = doc.get(k, 0) + v
            elif op == "$addToSet":
                for k, v in action.items():
                    arr = doc.setdefault(k, [])
                    if isinstance(v, dict) and "$each" in v:
                        for item in v["$each"]:
                            if item not in arr:
                                arr.append(item)
                    else:
                        if v not in arr:
                            arr.append(v)
            elif op == "$push":
                for k, v in action.items():
                    arr = doc.setdefault(k, [])
                    if isinstance(v, dict) and "$each" in v:
                        arr.extend(v["$each"])
                        if "$slice" in v:
                            arr[:] = arr[v["$slice"]:]
                    else:
                        arr.append(v)
        return type("Result", (), {"modified_count": 1})()

    async def find_one(self, filter):
        return self.store.get(filter["_id"])

    async def insert_one(self, doc):
        from copy import deepcopy
        self.store[doc["_id"]] = deepcopy(doc)
        return type("Result", (), {})()


@pytest.mark.asyncio
async def test_concurrent_track_stats():
    func.USERS_DB = DummyCollection()
    func.USERS_BUFFER.clear()
    user_id = 1

    async def update_task(i):
        await func.update_user(user_id, {
            "$inc": {"track_count": 1, "total_duration": 1000},
            "$addToSet": {"requesters": user_id},
            "$push": {"history": {"$each": [f"track_{i}"], "$slice": -25}}
        })

    await asyncio.gather(*(update_task(i) for i in range(10)))

    user = await func.get_user(user_id)
    assert user["track_count"] == 10
    assert user["total_duration"] == 10000
    assert user["requesters"] == [user_id]
    assert len(user["history"]) == 10
