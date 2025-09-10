"""MIT License

Copyright (c) 2023 - present Vocard Development

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Dict, List, Optional

import function as func


async def get_presets(user_id: int) -> Dict[str, List]:
    user = await func.get_user(user_id, "equalizer_presets")
    return user.get("equalizer_presets", {})


def _build_field(name: str) -> str:
    return f"equalizer_presets.{name}"


async def save_preset(user_id: int, name: str, levels: List) -> bool:
    return await func.update_user(user_id, {"$set": {_build_field(name): levels}})


async def delete_preset(user_id: int, name: str) -> bool:
    return await func.update_user(user_id, {"$unset": {_build_field(name): 1}})


async def get_preset(user_id: int, name: str) -> Optional[List]:
    presets = await get_presets(user_id)
    return presets.get(name)
