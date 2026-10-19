"""
main.py
Entry point for the Vehicle Black Box system.
Starts all sensor threads then launches the Flask web server.

Run on Pi:
    python main.py

Dashboard:  http://blackbox.local:5000
"""

import logging
import sensor_manager
from app import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-10s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("blackbox.log"),
    ],
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=" * 55)
    logger.info("  Vehicle Black Box — Starting up")
    logger.info("  VIT Chennai | B.Tech ECE")
    logger.info("=" * 55)

    # Start sensor acquisition threads
    sensor_manager.start_all()
    logger.info("All sensor threads launched.")

    # Start Flask (blocking)
    logger.info("Flask dashboard → http://blackbox.local:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
