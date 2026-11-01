# src/data_output.py
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def save_data(df, filepath):
    """Save a DataFrame as a CSV file."""

    # converts path and creates directory
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # save CSV without index
    df.to_csv(filepath, index=False)

    # logs number of rows
    logger.debug(f"Saved {len(df)} rows to {filepath}")
    
    return filepath