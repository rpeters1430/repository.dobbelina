import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hello() -> str:
    try:
        logger.info("Returning greeting message")
        return "Hello from Aider"
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
