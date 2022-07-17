import logging
import os

import uvicorn as uvicorn
from dotenv import load_dotenv
from src.core.logger import LOGGING

if __name__ == "__main__":
    # Приложение может запускаться командой
    # fastapi[all]
    # `uvicorn main:app --auth_host 0.0.0.0 --auth_port 8000`
    # но чтобы не терять возможность использовать дебагер,
    # запустим uvicorn сервер через python
    load_dotenv(
        os.path.dirname(os.path.dirname(os.path.abspath(__name__))) + "/.env_local"
    )
    uvicorn.run(
        os.getenv("UNICORN_PATH"),
        host=os.getenv("UNICORN_HOST"),
        port=int(os.getenv("UNICORN_PORT")),
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
