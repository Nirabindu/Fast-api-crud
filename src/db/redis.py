from redis import asyncio as aioredis

from src.config import Config

JTI_EXPIRY = 3600

token_blacklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
)


async def add_jit_to_blacklist(jti: str) -> None:
    await token_blacklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_blacklist(jti: str) -> bool:
    jti = await token_blacklist.get(jti)
    return jti is not None


# needs to handel redis connection if somehow it's stop
