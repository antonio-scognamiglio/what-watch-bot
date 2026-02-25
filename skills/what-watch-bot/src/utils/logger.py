import logging
import sys
import os

def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a logger that writes to the Docker CLI.
    If DEV_MODE=true, it bypasses OpenClaw's stderr swallowing by writing
    directly to PID 1's stdout stream (/proc/1/fd/1).
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        
        if dev_mode:
            log_stream = sys.stderr
            # Attempt to write directly to Docker's primary stdout stream
            try:
                if os.path.exists('/proc/1/fd/1') and os.access('/proc/1/fd/1', os.W_OK):
                    log_stream = open('/proc/1/fd/1', 'w')
            except Exception:
                pass

            handler = logging.StreamHandler(log_stream)
            formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False
        else:
            # Silence all logs if not in DEV_MODE
            logger.addHandler(logging.NullHandler())
            
    return logger
