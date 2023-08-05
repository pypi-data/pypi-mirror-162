from typing import Union, List, Dict

from interactions import Extension, extension_listener, Storage, OpCodeType, Snowflake, Client
import lavalink

from .models import VoiceState
from .websocket import VoiceWebSocketClient

__all__ = ["LavalinkVoice", "setup"]


class LavalinkVoice(Extension):
    def __init__(self, client: Client):
        self.client: Client = client
        self.lavalink_client: LavalinkClient = None  # type: ignore
        self._cache: Storage = self.client._http.cache[VoiceState]

        self.client.voice = self

    @extension_listener()
    async def on_start(self):
        self.lavalink_client = lavalink.Client(int(self.client.me.id))

    @extension_listener()
    async def on_raw_voice_server_update(self, data):
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink_client.voice_update_handler(lavalink_data)

    @extension_listener()
    async def on_raw_voice_state_update(self, data):
        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}
        await self.lavalink_client.voice_update_handler(lavalink_data)

    async def _connect_voice_channel(self, guild_id: int, channel_id: int, self_deaf: bool, self_mute: bool):
        payload = {
            "op": OpCodeType.VOICE_STATE,
            "d": {
                "channel_id": str(channel_id),
                "guild_id": str(guild_id),
                "self_deaf": self_deaf,
                "self_mute": self_mute
            }
        }
        await self.client._websocket._send_packet(payload)

    async def _disconnect_voice_channel(self, guild_id: int):
        payload = {
            "op": OpCodeType.VOICE_STATE,
            "d": {
                "channel_id": None,
                "guild_id": str(guild_id)
            }
        }
        await self.client._websocket._send_packet(payload)

    async def connect(
        self,
        guild_id: Union[Snowflake, int, str],
        channel_id: Union[Snowflake, int, str],
        self_deaf: bool = False,
        self_mute: bool = False
    ) -> lavalink.DefaultPlayer:
        """
        Connects to voice channel and creates player
        """
        await self._connect_voice_channel(guild_id, channel_id, self_deaf, self_mute)
        player = self.lavalink_client.player_manager.get(int(guild_id))
        if player is None:
            player = self.lavalink_client.player_manager.create(int(guild_id))
        return player

    async def disconnect(self, guild_id: Union[Snowflake, int]):
        await self._disconnect_voice_channel(int(guild_id))
        await self.lavalink_client.player_manager.destroy(int(guild_id))

    def get_player(self, guild_id: Union[Snowflake, int]) -> lavalink.DefaultPlayer:
        return self.lavalink_client.player_manager.get(int(guild_id))

    @property
    def voice_states(self) -> Dict[Snowflake, VoiceState]:
        return self._cache.values

    def get_user_voice_state(self, user_id: Union[Snowflake, int]) -> VoiceState:
        user_id = Snowflake(user_id) if isinstance(user_id, int) else user_id
        return self._cache.get(user_id)

    def get_channel_voice_states(self, channel_id: Union[Snowflake, int]) -> List[VoiceState]:
        channel_id = Snowflake(channel_id) if isinstance(channel_id, int) else channel_id
        return [voice_state for voice_state in self.voice_states.values() if voice_state.channel_id == channel_id]


def setup(client):
    return LavalinkVoice(client)
