import logging

logger = logging.getLogger(__name__)

class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        """Store a copy of the data and return a new integer ID."""
        
        # increase dataset integer id
        self._counter += 1
        dataset_id = self._counter

        # stores dataset based on id
        self._store[dataset_id] = {
            "filename": filename,
            "data": df.copy()
        }

        # logs stored dataset's id, rows, dataset id, size
        logger.debug(
            "Stored dataset: id=%s, rows=%s",
            dataset_id,
            len(df)
        )

        return dataset_id

    def get(self, dataset_id):
        """Return a copy of the stored DataFrame, or None."""
        # if dataset id doesn't exist, returns none
        if dataset_id not in self._store:
            return None

        # returns copy of dataset
        df = self._store[dataset_id]["data"].copy()

        logger.debug(
            "Retrieved dataset copy: id=%s, rows=%s",
            dataset_id,
            len(df)
        )

        return df

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        if dataset_id not in self._store:
            return None

        # ensures dataset is updated
        dataset = self._store[dataset_id]
        df = dataset["data"]

        return {
            "id": dataset_id,
            "filename": dataset["filename"],
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }



    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if
        missing."""
        if dataset_id not in self._store:
            return False

        self._store[dataset_id]["data"] = df.copy()

        logger.debug(
            "Updated dataset: id=%s, rows=%s",
            dataset_id,
            len(df)
        )

        # can modify df without changing the stored dataset, changes are saved only if you call update()

        return True

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0

    