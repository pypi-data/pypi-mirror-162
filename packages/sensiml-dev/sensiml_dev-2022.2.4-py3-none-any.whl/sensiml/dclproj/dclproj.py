import os
import sqlite3
import uuid
import wave
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pandas.core.frame import DataFrame
from sensiml.dclproj.datasegments import DataSegment, DataSegments
from sensiml.dclproj.utils import mfcc, plot_segments_labels


class DCLProject:
    def __init__(self):
        self._path = None
        self._conn = None
        self._tables = None
        self._verbose = False

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        if isinstance(value, bool):
            self._verbose = value
        else:
            print("verbose must be either True or False.")

    @property
    def data_dir(self) -> str:

        if self._path is None:
            raise Exception("Path is not set!")

        return os.path.join(self._path, "data")

    def _set_table_list(self):
        cursorObj = self._conn.cursor()

        cursorObj.execute('SELECT name from sqlite_master where type= "table"')

        self._tables = [x[0] for x in cursorObj.fetchall()]

    def create_connection(self, db_file: str) -> None:
        """create a database connection to the SQLite database specified by db_file

        :param db_file: database file
        :return: None
        """
        self._path = os.path.dirname(db_file)
        if not os.path.exists(db_file):
            print("database file not found at {}".format(db_file))
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)
            raise e

        self._conn = conn
        self._set_table_list()

    def _execute_query(self, query: str, header: str = None) -> DataFrame:

        cur = self._conn.cursor()

        if self.verbose:
            print(query)

        cur.execute(query)

        if header is None:
            header = [x[0] for x in cur.description]

        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append(row)

        df = pd.DataFrame(results, columns=header)

        if "uuid" in header:
            df["uuid"] = df["uuid"].apply(
                lambda x: uuid.UUID(bytes_le=x) if x else None
            )

        if "last_modified" in header:
            df["last_modified"] = pd.to_datetime(df["last_modified"])

        if "created_at" in header:
            df["created_at"] = pd.to_datetime(df["created_at"])

        if "local_status" in header:
            local_status = {
                0: "To Add",
                1: "To Update",
                "Synced": "Synced",
                2: "To Delete",
                None: "Synced",
            }
            df["local_status"] = (
                df["local_status"].fillna("Synced").apply(lambda x: local_status[x])
            )

        return df

    def _list_table_raw(self, tablename: str) -> DataFrame:

        if tablename not in self._tables:
            print("Table is not part of the database.")
            return None

        query = "SELECT * FROM {tablename} ".format(tablename=tablename)

        return self._execute_query(query)

    def _list_table(
        self,
        tablename: str,
        fields: List[str],
        fk_fields: Optional[Dict] = None,
        query_filter: Optional[str] = None,
    ):

        if tablename not in self._tables:
            print("Table is not part of the database.")
            return None

        select_fields = ", ".join(
            ["{}.{}".format(tablename, field) for field in fields]
        )

        if fk_fields:
            select_fields += ", " + ", ".join(
                [
                    "{}.name".format(fk_table)
                    if fk_table != "LabelValue"
                    else "{}.value".format(fk_table)
                    for fk_table in fk_fields.keys()
                ]
            )

        query_select = "SELECT {select_fields} FROM {tablename} ".format(
            select_fields=select_fields, tablename=tablename
        )

        query_join = ""

        if fk_fields:
            join_fields = []
            for fk_table, fk_field in fk_fields.items():
                join_fields.append(
                    "JOIN {fk_table} ON {fk_table}.id = {tablename}.{fk_field} ".format(
                        fk_table=fk_table, tablename=tablename, fk_field=fk_field
                    )
                )
            query_join += " ".join(join_fields)

        header = None

        if query_filter:
            query_where = (
                query_filter  # + "AND {}.local_status != 2 ".format(tablename)
            )
        else:
            query_where = ""  # "WHERE {}.local_status != 2 ".format(tablename)

        if fk_fields:
            header = fields + list(fk_fields.values())

        return self._execute_query(query_select + query_join + query_where, header)

    def _list_captures_metadata(self) -> DataFrame:
        """returns a dataframe containing the capture name and the associated metadata"""

        fields = ["uuid"]

        fk_fields = OrderedDict(
            [("Capture", "capture"), ("LabelValue", "label_value"), ("Label", "label")]
        )

        df = self._list_table("CaptureMetadataValue", fields, fk_fields=fk_fields)

        M = []
        for capture_name in df.capture.unique():
            caps_dict = df[df.capture == capture_name][
                ["label", "label_value"]
            ].to_dict(orient="records")
            tmp = {"capture": capture_name}
            for item in caps_dict:
                tmp[item["label"]] = item["label_value"]
            M.append(tmp)

        return DataFrame(M).fillna("")

    def list_captures(self, include_metadata: bool = True) -> DataFrame:
        """List the captures in the DCLI project file

        Args:
            include_metadata (bool, optional): If True return the associated metadata information with each capture. Defaults to True.

        Returns:
            DataFrame: DataFrame containing the capture information
        """

        fields = [
            "uuid",
            "name",
            "file_size",
            "number_samples",
            "set_sample_rate",
            "created_at",
            "local_status",
            "last_modified",
        ]

        fk_fields = OrderedDict([("CaptureConfiguration", "capture_configuration")])

        df = self._list_table("Capture", fields=fields, fk_fields=fk_fields)

        if not include_metadata:
            return df

        return df.merge(
            self._list_captures_metadata(), left_on="name", right_on="capture"
        ).drop("capture", axis=1)

    def list_sessions(self) -> DataFrame:
        fields = [
            "id",
            "name",
            "parameters",
            "custom",
            "preprocess",
            "created_at",
            "local_status",
            "last_modified",
        ]

        fk_fields = OrderedDict([])

        return self._list_table("Segmenter", fields, fk_fields)

    def list_capture_segments(
        self, captures: Optional[List] = None, sessions: Optional[List] = None
    ) -> DataFrame:
        """Returns a DataFrame of segment information that are in the captures and sessions specified

        Args:
            captures (Optional[List], optional): A list of captures to return segments about. Defaults to None.
            sessions (Optional[List], optional): A list of sessions to return segments for. Defaults to None.

        Returns:
            DataFrame:
        """

        if captures is not None and isinstance(captures, str):
            captures = [captures]
        if sessions is not None and isinstance(sessions, str):
            sessions = [sessions]

        query_filter = ""

        def create_select(select):
            return ", ".join(['"{}"'.format(x) for x in select])

        if captures and sessions:
            query_filter = "WHERE Capture.name in ({}) ".format(
                create_select(captures)
            ) + "AND Segmenter.name in ({0}) ".format(create_select(sessions))

        elif captures:
            query_filter = "WHERE Capture.name in ({}) ".format(create_select(captures))
        elif sessions:
            query_filter += "WHERE Segmenter.name in ({0}) ".format(
                create_select(sessions)
            )

        fields = [
            "uuid",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "local_status",
            "created_at",
            "last_modified",
        ]

        fk_fields = OrderedDict(
            [
                ("Segmenter", "segmenter"),
                ("Capture", "capture"),
                ("LabelValue", "label_value"),
            ]
        )

        return (
            self._list_table("CaptureLabelValue", fields, fk_fields, query_filter)
            .reset_index(drop=True)
            .sort_values(by=["capture", "segmenter", "capture_sample_sequence_start"])
        )

    def get_capture_metadata(self, capture: str) -> DataFrame:
        """Gets the metadata for the specified capture

        Args:
            capture (str): name of the capture file

        Returns:
            DataFrame: DataFrame containing the metadata associated with this capture
        """

        fields = ["uuid"]

        fk_fields = OrderedDict(
            [("Capture", "capture"), ("LabelValue", "label_value"), ("Label", "label")]
        )

        df = self._list_table("CaptureMetadataValue", fields, fk_fields=fk_fields)

        return df[df["capture"] == capture]

    def get_capture_segments(
        self, captures: Optional[List] = None, sessions: Optional[List] = None
    ):
        """
        Returns a DataSegment object of the specified capture and session


        Args:
            capture_name (str): name of capture
            session (str):  name of session where the labels are
        """
        if captures is not None and isinstance(captures, str):
            captures = [captures]
        if sessions is not None and isinstance(sessions, str):
            sessions = [sessions]

        labels = self.list_capture_segments(captures=captures, sessions=sessions)

        M = DataSegments()

        cached_df = None
        capture_index = 4
        for index, label in enumerate(
            labels[
                [
                    "capture_sample_sequence_start",
                    "capture_sample_sequence_end",
                    "uuid",
                    "label_value",
                    "capture",
                    "segmenter",
                ]
            ].values
        ):
            # TODO: read wave file if file is .wav#
            if cached_df != label[capture_index]:
                tmp_df = self.get_capture(label[capture_index])
                cached_df = label[capture_index]

            M[index] = DataSegment(
                tmp_df.loc[label[0] : label[1]],
                segment_id=index,
                session=label[5],
                label_value=label[3],
                uuid=label[2],
                capture=label[4],
            )

        return M

    def get_capture(self, capture_name: str) -> DataFrame:
        """
        Returns the capture as a dataframe

        Args:
            capture_name (str): name of capture
        """

        # TODO: read wave file if file is .wav
        ext = capture_name.split(".")[-1]

        if ext == "csv":
            tmp_df = pd.read_csv(
                os.path.join(self.data_dir, capture_name), index_col="sequence"
            )
        elif ext == "wav":
            with wave.open(
                os.path.join(self.data_dir, capture_name), "rb"
            ) as wave_reader:
                waveFrames = wave_reader.readframes(wave_reader.getnframes())
                waveData = np.fromstring(waveFrames, dtype=np.int16).reshape(
                    (-1, wave_reader.getnchannels())
                )
                columns = [
                    "channel_{}".format(i) for i in range(wave_reader.getnchannels())
                ]
                tmp_df = DataFrame(waveData, columns=columns).rename_axis(
                    index="sequence"
                )

        return tmp_df

    def get_captures(self, capture_names: Optional[List[str]] = None) -> DataFrame:
        """
        Returns the capture as a list of dataframes

        Args:
            capture_names (List[str]): name of captures to return, if None returns all captures
        """
        if capture_names is None:
            capture_names = os.listdir(self.data_dir)

        return {
            capture_name: self.get_capture(capture_name)
            for capture_name in capture_names
        }

    def plot_segment_labels(
        self,
        capture_names: List[str],
        session: str,
        columns: Optional[List[str]] = None,
        transforms: Optional[List[Dict]] = None,
        figsize: Tuple = (30, 8),
        ylim: Optional[Tuple] = None,
    ) -> None:
        """
        Creates a plot of the labels and raw signal data for a session and one or more capture files.

        Args:
            capture_names (List[str]): List if captures to plot
            session (str):  name of session to pull the labels from
            columns (list): a list of columns to plot from the data
             label the value is the label it was should be renamed to
            transforms: additional fucntions to apply prior to plotting the data


        Examples:
            >>> def sum_columns(x):
            >>>     return x[['Column1', 'Column2']].sum()

            >>> func = {'name':'sum','func':sum_columns, 'type':'transform'}

            >>> dcl.plot_segment_labels(captures, session_name, columns=['sum], transforms=[func])

            >>> # example of multiple transforms executed in order

            >>> def sum_columns(x):
            >>>     return x[['Column1', 'Column2']].sum()

            >>> def remove_offset(x):
            >>>    x['Column1']-=100
            >>>    x['Column2']-=200
            >>>    return x

            >>> func2 = {'name':'filter','func':remove_offset, "type":'filter', "columns":['Column1', 'Column2']}
            >>> func1 = {'name':'sum','func':sum_columns, "type":'transform'}

            >>> dcl.plot_segment_labels(captures, session_name, columns=['Column1', 'Column2', 'sum'], transforms=[func1, func2])
        """

        sessions = self.list_sessions()
        session_id = sessions[sessions.name == session].id.values[0]
        clv = self._list_table_raw("CaptureLabelValue")
        label_value_ids = clv[clv.segmenter == session_id].label_value.unique()
        lv = self._list_table_raw("LabelValue")
        labels = sorted(lv[lv.id.isin(label_value_ids)].value.values.tolist())
        class_map = {label: index for index, label in enumerate(labels)}

        M = []
        current_start = 0

        plt.figure(figsize=figsize)
        currentAxis = plt.gca()

        if isinstance(capture_names, str):
            capture_names = [capture_names]

        for capture_name in capture_names:

            segments = self.list_capture_segments(
                captures=[capture_name], sessions=[session]
            )
            capture = self.get_capture(capture_name)
            M.append(capture)

            plot_segments_on_capture(
                capture,
                segments,
                capture_name=capture_name,
                labels=list(class_map.keys()),
                current_start=current_start,
                ylim=ylim,
                figsize=figsize,
                currentAxis=currentAxis,
            )

            current_start += capture.shape[0]

        capture = pd.concat(M)

        if transforms is not None:
            for func in transforms:
                if func["type"] == "transform":
                    capture[func["name"]] = capture.apply(
                        lambda x: func["func"](x), axis=func.get("axis", 1)
                    )

                if func["type"] == "filter":
                    capture[func["columns"]] = capture.apply(
                        lambda x: func["func"](x), axis=func.get("axis", 1)
                    )

        if columns is None:
            columns = capture.columns

        capture[columns].reset_index(drop=True).plot(
            figsize=figsize,
            ax=currentAxis,
            title="session: '{session}'".format(capture=capture_name, session=session),
            ylim=ylim,
        )

        return capture.reset_index(drop=True)

    def plot_frequency(
        self,
        capture_name: str,
        channel: str,
        sample_freq: int = 16000,
        figsize: Tuple = (30, 4),
        session: Optional[str] = None,
    ):

        nrows = 3
        data = self.get_capture(capture_name)

        fig, axes = plt.subplots(
            nrows=nrows, ncols=1, figsize=(figsize[0], figsize[1] * nrows)
        )
        fig.tight_layout()

        data.plot(ax=axes[0], title=capture_name, xlim=(0, data.shape[0]), xlabel="")

        _ = axes[1].specgram(data[channel], NFFT=512)
        axes[1].set_title("Sepctrogram")

        axes[2].imshow(
            mfcc(data, channel, sample_freq=sample_freq, plot_all=False), aspect="auto"
        )
        axes[2].set_title("MFCC")

        if session:
            segments = self.list_capture_segments(
                captures=[capture_name], sessions=[session]
            )

            plot_segments_labels(
                segments,
                axes=axes[0],
                y_label=(
                    data[channel].min(),
                    int(data[channel].max()) - int(data[channel].min()),
                ),
            )

        plt.subplots_adjust(hspace=0.2)

        return axes


def plot_segments_on_capture(
    capture,
    segments,
    capture_name,
    labels=None,
    current_start=0,
    ylim=None,
    figsize: Tuple = (30, 8),
    currentAxis=None,
):

    if currentAxis is None:
        plt.figure(figsize=figsize)
        currentAxis = plt.gca()

    cmap = plt.cm.rainbow

    if labels is None:
        labels = segments.label_value.unique().tolist()

    delta = 1 / len(labels)
    label_float = np.arange(0, 1, delta)
    label_float[-1] = 1.0

    label_colors = {labels[index]: cmap(x) for index, x in enumerate(label_float)}
    label_legend = [Line2D([0], [0], color=cmap(x), lw=4) for x in label_float] + [
        Line2D([0], [0], color="white", lw=4)
    ]

    for _, seg in segments.iterrows():
        y_origin = capture.describe().loc["min"].min() if ylim is None else ylim[0]
        x_origin = seg["capture_sample_sequence_start"] + current_start
        x_final = (
            seg["capture_sample_sequence_end"] - seg["capture_sample_sequence_start"]
        )
        y_final = (
            capture.describe().loc["max"].max() - y_origin
            if ylim is None
            else ylim[1] - ylim[0]
        )

        currentAxis.add_artist(
            plt.Rectangle(
                (x_origin, y_origin),
                x_final,
                y_final,
                alpha=0.2,
                color=label_colors[seg["label_value"]],
            )
        )

    currentAxis.legend(label_legend, labels + [""])

    currentAxis.text(
        current_start,
        0 if ylim is None else ylim[0],
        capture_name,
        style="italic",
        rotation=90,
        # bbox={"facecolor": "grey", "alpha": 0.5, "pad": 10},
    )
