import asyncio
import json
from app.agents.orchestrator import Concierge
from app.core.config import settings


async def main():
    result = await Concierge(settings).preflight()
    print(json.dumps(result, indent=2))
    return 0 if result["agent_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
