"""
Atribución — Runner de todos los guardianes.

Arranca los 9 guardianes en paralelo y mantiene el proceso vivo.

Uso:
    python -m guards.runner
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys

from guards import ALL_GUARDS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("guards.runner")


async def main() -> None:
    """Arranca todos los guardianes y espera hasta Ctrl+C."""
    guards = [g() for g in ALL_GUARDS]

    logger.info("Arrancando %d guardianes...", len(guards))
    for g in guards:
        await g.start()

    # Esperar señal
    stop_event = asyncio.Event()

    def _handle_signal(*_args):
        logger.info("Señal recibida. Deteniendo...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_signal)

    await stop_event.wait()

    for g in guards:
        await g.stop()

    logger.info("Todos los guardianes detenidos.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)