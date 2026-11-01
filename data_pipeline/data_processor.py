# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    
    # drops duplicate rows
    result = df.drop_duplicates()

    # logs original vs. new count of rows
    logger.debug(f"remove_duplicates: {len(df)} --> {len(result)} rows")
    return result


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""

    # checks if axis is rows, logs before vs. after dropping missing rows
    if axis == "rows":
        result = df.dropna(axis=0)
        logger.debug(f"handle_missing: {len(df)} --> {len(result)} rows")

    # checks if axis is cols, logs before vs. after dropping missing cols
    elif axis == "columns":
        result = df.dropna(axis=1)
        logger.debug(f"handle_missing: {len(df.columns)} --> {len(result.columns)} columns")
    
    # if not rows or cols, raises error because axis is unsupported
    else:
        logger.error(f"Unsupported axis: {axis}")
        raise ValueError(f"Unsupported axis: {axis}")
    return result


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""

    # check if method is iqr or zscore
    if method not in ("iqr", "zscore"):
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df

    # loops over columns and warns/continues if column missing/non-numeric
    for col in columns:
        if col not in result.columns:
            logger.warning(f"Column not found: {col}")
            continue
        if not pd.api.types.is_numeric_dtype(result[col]):
            logger.warning(f"Column is not numeric: {col}")
            continue

        # computes upper and lower bounds for iqr or zscore
        series = result[col]
        if method == "iqr":
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
        else:
            mean, std = series.mean(), series.std()
            if pd.isna(std):  # fewer than 2 values
                std = 0
            lower, upper = mean - threshold * std, mean + threshold * std

        # keeps rows within calculated bounds
        keep = series.between(lower, upper) | series.isna()
        removed = (~keep).sum()
        result = result[keep]

        # logs column, method, threshold, bounds, and rows removed
        logger.debug(
            f"{col}: method={method}, threshold={threshold}, "
            f"lower={lower}, upper={upper}, removed={removed}"
        )

    return result


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    # reads the config
    settings = config["processing"]
    result = df

    # checks which functions are enabled and calls in order
    if settings.get("remove_duplicates"):
        result = remove_duplicates(result)

    missing = settings.get("missing", {})
    if missing.get("enabled"):
        result = handle_missing(result, axis=missing["axis"])

    outliers = settings.get("outliers", {})
    if outliers.get("enabled"):
        result = remove_outliers(
            result,
            columns=outliers["columns"],
            method=outliers["method"],
            threshold=outliers["threshold"],
        )

    return result


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    # returns summary of rows/columns before/after/count removed from cleaning
    return {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns),
    }