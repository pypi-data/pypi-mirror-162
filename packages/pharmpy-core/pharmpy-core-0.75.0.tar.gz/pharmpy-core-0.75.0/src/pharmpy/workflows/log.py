import datetime
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class LogEntry:
    category: str = None
    time: datetime.datetime = datetime.datetime.now()
    model: str = ""
    tool: str = ""
    task: str = ""
    path: Path = None
    message: str = ""


class Log:
    """Timestamped error and warning log"""

    def __init__(self):
        self._log = []  # list of LogEntry

    @property
    def log(self):
        return self._log

    def log_error(self, message):
        """Log an error

        Parameters
        ----------
        message : str
            Error message
        """
        entry = LogEntry(category='ERROR', message=message)
        self._log.append(entry)

    def log_warning(self, message):
        """Log a warning

        Parameters
        ----------
        message : str
            Warning message
        """
        entry = LogEntry(category='WARNING', message=message)
        self._log.append(entry)

    def to_dataframe(self):
        """Create an overview dataframe from log

        Returns
        -------
        pd.DataFrame
            Dataframe with overview of log entries
        """
        categories = [entry.category for entry in self._log]
        times = [entry.time for entry in self._log]
        models = [entry.model for entry in self._log]
        tools = [entry.tool for entry in self._log]
        tasks = [entry.task for entry in self._log]
        paths = [entry.path for entry in self._log]
        messages = [entry.message for entry in self._log]
        df = pd.DataFrame(
            {
                'category': categories,
                'time': times,
                'model': models,
                'tool': tools,
                'task': tasks,
                'path': paths,
                'message': messages,
            }
        )
        return df

    def __repr__(self):
        s = ''
        for entry in self._log:
            s += f'{entry.category:<8} {entry.time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            for line in entry.message.split('\n'):
                s += f'    {line}\n'
        return s
