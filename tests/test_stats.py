import types
import logging
import asyncio
import pytest

import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# ensure settings.json exists for imports
settings_path = os.path.join(PROJECT_ROOT, 'settings.json')
if not os.path.exists(settings_path):
    with open(settings_path, 'w', encoding='utf8') as f:
        json.dump({}, f)

import voicelink.player as player_module
from voicelink.objects import Track

class DummyBot:
    def __init__(self):
        self.ipc = types.SimpleNamespace(_is_connected=False)
    def dispatch(self, *args, **kwargs):
        pass

class DummyNode:
    def __init__(self, bot):
        self.bot = bot
        self._players = {}
        self._logger = logging.getLogger("test")
        self.yt_ratelimit = None
    async def send(self, *args, **kwargs):
        pass
    async def get_recommendations(self, *args, **kwargs):
        return []

def test_track_end_stats_duration(monkeypatch):
    async def run_test():
        bot = DummyBot()
        node = DummyNode(bot)
        # Ensure NodePool.get_node returns our dummy node
        monkeypatch.setattr(player_module.NodePool, "get_node", classmethod(lambda cls: node))

        called = {}
        async def mock_track_end_stats(guild_id, duration):
            called["guild_id"] = guild_id
            called["duration"] = duration
        monkeypatch.setattr(player_module.func, "track_end_stats", mock_track_end_stats, raising=False)
        dummy_settings = types.SimpleNamespace(
            max_queue=100,
            controller={},
            bot_access_user=set(),
            voice_status_template=None,
            sources_settings={"others": {}}
        )
        monkeypatch.setattr(player_module.func, "settings", dummy_settings, raising=False)
        monkeypatch.setattr(player_module, "Placeholders", lambda *args, **kwargs: types.SimpleNamespace(variables={}))
        import voicelink.objects as objects_module
        monkeypatch.setattr(objects_module, "extract", lambda url: types.SimpleNamespace(domain="test"), raising=False)

        class DummyGuild:
            id = 987
            name = "guild"
        class DummyChannel:
            guild = DummyGuild()
            id = 123
            members = []
        class DummyCtx:
            author = types.SimpleNamespace(id=111, bot=False)
            guild = DummyGuild()

        player = player_module.Player(bot, DummyChannel(), DummyCtx(), {})

        # simulate time progression: start at 1000s, end at 1005s
        times = [1000.0, 1005.0, 1010.0]
        monkeypatch.setattr(player_module.time, "time", lambda: times.pop(0))

        track = Track(track_id="x", info={"identifier": "id", "length": 10000, "title": "t", "author": "a", "uri": "u", "sourceName": "x"}, requester=DummyCtx.author)
        player._current = track
        await player._dispatch_event({"type": "TrackStartEvent"})
        player._ending_track = track
        await player._dispatch_event({"type": "TrackEndEvent", "reason": "finished"})

        assert called["duration"] == 5000
        assert called["guild_id"] == 987

    asyncio.run(run_test())

