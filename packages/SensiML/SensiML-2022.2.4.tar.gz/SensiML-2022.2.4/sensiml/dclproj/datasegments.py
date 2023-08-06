import json
import os
from typing import Dict, List, Optional, Tuple, Type

import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame
from sensiml.dclproj.utils import mfcc


class DataSegment(object):
    def __init__(
        self,
        data: DataFrame,
        segment_id: int,
        session: str,
        label_value: Optional[str] = None,
        uuid: Optional[str] = None,
        capture: Optional[str] = None,
    ):
        self._metadata = [
            "label_value",
            "capture",
            "segment_id",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "columns",
            "session",
            "uuid",
        ]
        self._label_value = str(label_value)
        self._session = session
        self._segment_id = segment_id
        self._uuid = uuid
        self._original_index = data.index
        self._capture = capture
        self._data = data.reset_index(drop=True)

    def plot(self, figsize: Tuple = (30, 4), **kwargs):
        self._data.plot(
            title=self.__str__(),
            figsize=figsize,
            xlim=(0, self._data.shape[0]),
            **kwargs
        )

    def plot_spectrogram(
        self, channel: str, fft_length: int = 512, figsize: Tuple = (30, 4), **kwargs
    ):
        """Plots the spectrogram for the signal.

        Args:
            channel (str): the channel/column of sensor data to use
            fft_length (int, optional): The size of the FTT length to use when computing the spectrogram. Defaults to 512.
            figsize (Tuple, optional): the size of the figure that will be created. Defaults to (30, 4).
        """

        fig, axis = plt.subplots(figsize=figsize)

        data = axis.specgram(self._data[channel], NFFT=fft_length, **kwargs)

    def plot_mfcc(
        self, channel: str, sample_freq: int = 16000, figsize: Tuple = (30, 4)
    ):
        """Plots the MFCC spectrogram for the signal.

        Args:
            channel (str): the channel/column of sensor data to use
            sample_freq (int, optional): The frequency of the sample data. Defaults to 1600.
            figsize (Tuple, optional): the size of the figure that will be created. Defaults to (30, 4).
        """
        fig, axis = plt.subplots(figsize=figsize)

        _ = axis.imshow(
            mfcc(self._data, channel, sample_freq=sample_freq, plot_all=False),
            aspect="auto",
        )

    def plot_frequency(
        self, channel: str, sample_freq: int = 16000, figsize: Tuple = (30, 8), **kwargs
    ):
        """Plots the signal data, the spectrogram and the MFCC spectrogram.

        Args:
            channel (str): the channel/column of sensor data to use
            sample_freq (int, optional): The frequency of the sample data. Defaults to 1600.
            figsize (Tuple, optional): the size of the figure that will be created. Defaults to (30, 4).
        """

        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=figsize)

        self._data.plot(
            title=self.__str__(), ax=axes[0], xlim=(0, self._data.shape[0]), **kwargs
        )

        data = axes[1].specgram(self._data[channel], NFFT=512, **kwargs)

        axes[2].imshow(
            mfcc(self._data, channel, sample_freq=sample_freq, plot_all=False),
            aspect="auto",
        )
        axes[2].set_title("MFCC")

        plt.subplots_adjust(hspace=0.2)

    @property
    def capture(self):
        return self._capture

    @property
    def segment_id(self):
        return self._segment_id

    @property
    def label_value(self):
        return self._label_value

    @property
    def uuid(self):
        return str(self._uuid)

    @property
    def data(self):
        return self._data

    @property
    def segment_length(self):
        return int(self._data.shape[0])

    @property
    def columns(self):
        return int(self._data.shape[1])

    @property
    def capture_sample_sequence_start(self):
        return int(self._original_index[0])

    @property
    def capture_sample_sequence_end(self):
        return int(self.capture_sample_sequence_start + self.segment_length)

    @property
    def start(self):
        return self.capture_sample_sequence_start

    @property
    def end(self):
        return self.capture_sample_sequence_end

    @property
    def session(self):
        return self._session

    @property
    def metadata(self):
        return {metadata: getattr(self, metadata) for metadata in self._metadata}

    def to_dict(self):
        return self.metadata

    def __str__(self):
        return " ".join(["{}: {}, ".format(k, v) for k, v in self.metadata.items()])


class DataSegments(dict):
    """DataSegments is a dictionary of DataSegment objects with additional APIs"""

    def plot(self, **kwargs):

        plt.rcParams.update({"figure.max_open_warning": 0})
        for _, segment in self.items():
            segment.plot(**kwargs)

    def to_dataframe(self) -> DataFrame:
        """Returns a dataframe representation of the segment information."""

        M = []
        for _, segment in self.items():
            M.append(segment.metadata)

        tmp_df = DataFrame(M)
        tmp_df["length"] = (
            tmp_df["capture_sample_sequence_end"]
            - tmp_df["capture_sample_sequence_start"]
        )
        return tmp_df.sort_values(
            by=["session", "capture", "capture_sample_sequence_start"]
        ).reset_index(drop=True)

    def to_dict(self, orient: str = "records") -> Dict:
        """Returns a dictionary representation of the DataSegments object

        Args:
            orient (str): defaults to records
        """

        return self.to_dataframe().to_dict(orient=orient)

    def export(self, folder: str = "segment_export"):
        """Exports all the segments to the specified folder as individual <UUID>.csv files.
        The metadata is stored in a metadata.json file which has all the info about each segment.

        Args:
            folder (str, optional): The folder to export to. Defaults to "segment_export".
        """

        if not os.path.exists(folder):
            os.mkdir(folder)

        metadata = []
        for _, segment in self.items():
            segment.data.to_csv(os.path.join(folder, segment.uuid + ".csv"), index=None)
            metadata.append(segment.metadata)

        json.dump(metadata, open(os.path.join(folder, "metadata.json"), "w"))

    def to_dcli(
        self, filename: Optional[str] = None, session: Optional[str] = None
    ) -> List:
        """Creates a .dcli file describing the segment information that can be imported into the Data Capture Lab

        Args:
            filename (Optional[str], optional): The name of the file to save it to, if None no file is created.. Defaults to None.
            session (Optional[str], optional): The name of a session to use when creating the DCLI file. if None the session from the DataSegment objects are used.. Defaults to None.

        Returns:
            List: DCLI formatted segments
        """

        def get_capture_index(dcli_capture, file_name):
            for index, capture in enumerate(dcli_capture):
                if file_name == capture["file_name"]:
                    return index

            return None

        def get_session_index(sessions, session_name):
            for index, session in enumerate(sessions):
                if session_name == session["session_name"]:
                    return index

            return None

        dcli_capture = []

        for _, segment in self.items():

            capture_index = get_capture_index(dcli_capture, segment.capture)

            if capture_index is None:
                dcli_capture.append({"file_name": segment.capture, "sessions": []})
                capture_index = -1

            session_index = get_session_index(
                dcli_capture[capture_index]["sessions"],
                segment.session if session is None else session,
            )

            if session_index is None:
                if session is None:
                    dcli_capture[capture_index]["sessions"].extend(
                        [{"session_name": segment.session, "segments": []}]
                    )
                else:
                    dcli_capture[capture_index]["sessions"].extend(
                        [{"session_name": session, "segments": []}]
                    )

                session_index = -1

            dcli_capture[capture_index]["sessions"][session_index]["segments"].append(
                {
                    "name": "Label",
                    "value": segment.label_value,
                    "start": segment.start,
                    "end": segment.end,
                }
            )

        if filename is not None:
            json.dump(dcli_capture, open(filename, "w"))

        return dcli_capture

    def to_audacity(self, rate: int = 16000) -> List:
        """Creates multiple files with the naming convention file_{capture_name}session{session_name}.txt.

        These can be imported into Audacity directly going to File->Import->Labels

        Args:
            rate (int): Audacity uses the actual time and note number of samples. Set the rate to the sample rate for the captured date. Default is 16000.
        """

        dcli = self.to_dcli()

        for capture in dcli:
            for session in capture["sessions"]:
                outfile = "file_{capture}_session_{session}.txt".format(
                    capture=capture["file_name"], session=session["session_name"]
                )
                with open(
                    outfile,
                    "w",
                ) as out:
                    for segment in session["segments"]:
                        out.write(
                            "{start_time}\t{end_time}\t{label}\n".format(
                                start_time=segment["start"] / rate,
                                end_time=segment["end"] / rate,
                                label=segment["value"],
                            )
                        )
                    print("labels written to {outfile}".format(outfile=outfile))

    @property
    def label_values(self) -> List:
        """List all the labels in the DataSegments object"""

        label_values = set()
        for _, segment in self.items():
            label_values.add(segment.label_value)

        return list(label_values)

    def merge_label_values(self, data_segments: dict) -> List:
        """Merges label values between to data segments.

        Args:
            data_segments (dict): The datasegment object to merge label values with

        Returns:
            List: The sorted union of the label values from both datasegments
        """

        return sorted(
            list(set(data_segments.label_values).union(set(self.label_values)))
        )

    def merge_segments_df(self, delta: int = 1) -> DataFrame:
        """Merge segments that overlap or are within delta of each other.

        Args:
            delta (int, optional): The distance between two nonoverlapping segments where they will still be merged. Defaults to 1.

        Returns:
            DataFrame: A DataFrame consisting of the merged segments
        """

        return merge_segments(self, delta=delta)

    def merge_segments(self, dcl, delta: int = 0):
        """Merge segments that overlap or are within delta of each other.

        Args:
            dcl (DCLProject): A DCLProject object that is connected to the DCLI file
            delta (int, optional): The distance between two nonoverlapping segments where they will still be merged. Defaults to 1.

        Returns:
            DataSegments: A DataSegments object consisting of the merged segments
        """

        merged_segments = merge_segments(self, delta=delta)

        return segment_list_to_datasegments(dcl, merged_segments)

    def filter_segments_df(self, min_length: int) -> DataFrame:
        """Filters out segments below a minimum length

        Args:
            min_length (int): Segments below this will be filtered

        Returns:
            DataFrame: A DataFrame consisting of the segments not filtered
        """

        return filter_segments(self, min_length=min_length)

    def filter_segments(self, dcl, min_length: int):
        """Filters out segments below a minimum length

        Args:
            dcl (DCLProject): A DCLProject object that is connected to the DCLI file
            min_length (int): Segments below this will be filtered

        Returns:
            DataSegments: A DataSegments object consisting of the merged segments
        """

        filtered_segments = filter_segments(self, min_length=min_length)

        return segment_list_to_datasegments(dcl, filtered_segments)

    def remove_overlap_df(self) -> DataFrame:
        """Removes the overlap between segments by setting the segment start and
        end of overlapping segments to the same point, halfway between the overlapping edges.

        Returns:
            DataFrame: A DataFrame consisting of the segments not filtered
        """

        return remove_overlap(self)

    def remove_overlap(self, dcl):
        """Removes the overlap between segments by setting the segment start and
        end of overlapping segments to the same point, halfway between the overlapping edges.

        Args:
            dcl (DCLProject): A DCLProject object that is connected to the DCLI file

        Returns:
            DataSegments: A DataSegments object consisting of the merged segments
        """
        filtered_segments = remove_overlap(self)

        return segment_list_to_datasegments(dcl, filtered_segments)

    def join_segments_df(self, delta: Optional[int] = None) -> DataFrame:
        """Joins adjacent segments so that there is no empty space between segments.

        Args:
            delta (int): Segments outside this range will not be joined. If None, all neighboring segments will be merged regardless of the distance. Default is None.

        Returns:
            DataFrame: A DataFrame consisting of the segments not filtered
        """

        return join_segments(self)

    def join_segments(self, dcl, delta: Optional[int] = None):
        """Joins adjacent segments so that there is no empty space between segments.

        Args:
            dcl (DCLProject): A DCLProject object that is connected to the DCLI file
            delta (int): Segments outside this range will not be joined. If None, all neighboring segments will be merged regardless of the distance. Default is None.

        Returns:
            DataSegments: A DataSegments object consisting of the merged segments
        """

        joined_segments = join_segments(self)

        return segment_list_to_datasegments(dcl, joined_segments)


def to_datasegments(data, metdata_columns: list, label_column: str):
    """Converts a dataframe into a data segments object

    Args:
        data (DataFrame): The dataframe to convert to a DataSegments object
        metdata_columns (list): List of metadata columns
        label_column (str): The name of the column that contains information about the Label

    Returns:
        DataSegments: A DataSegments object
    """

    group_columns = metdata_columns + [label_column]
    g = data.groupby(group_columns)
    ds = DataSegments()

    data_columns = [x for x in data.columns if x not in group_columns]

    for key in g.groups.keys():

        metadata = {}
        for index, value in enumerate(group_columns):
            metadata[value] = key[index]

        tmp_df = g.get_group(key)[data_columns]

        ds[tmp_df["uuid"]] = DataSegment(tmp_df, metadata, metadata[label_column])

    return ds


def segment_list_to_datasegments(dcl, labels: DataFrame, session: str = ""):
    """Converts a DataFrame of segments into a DataSegments object

    Args:
        dcl (DCLProject): A DCLProject object that is connected to the DCLI file
        labels (DataFrame): A dataframe containing the segment information
        session (str, optional): The session to set the segments too. Defaults to "".

    Returns:
        DataSegments
    """

    if isinstance(labels, DataFrame):

        # DCL generates segments with this format ""
        if labels.columns.to_list() == [
            "File",
            "Label",
            "Start",
            "End",
            "Length",
        ]:
            label_dict = (
                labels.rename(
                    columns={
                        "File": "capture",
                        "Label": "label_value",
                        "Start": "capture_sample_sequence_start",
                        "End": "capture_sample_sequence_end",
                    },
                )
                .sort_values(by="capture")
                .to_dict(orient="records")
            )
        else:
            label_dict = labels.sort_values(
                by=["capture", "session", "capture_sample_sequence_start"]
            ).to_dict(orient="records")
    else:
        raise Exception("Expected DataFrame")

    data_segments = DataSegments()
    capture_name = None

    for index, label in enumerate(label_dict):

        if capture_name != label["capture"]:
            data = dcl.get_capture(label["capture"])
            capture_name = label["capture"]

        tmp_df = data.iloc[
            label["capture_sample_sequence_start"] : label[
                "capture_sample_sequence_end"
            ]
        ]

        data_segments[index] = DataSegment(
            tmp_df,
            index,
            session=label.get("session", session),
            label_value=label["label_value"],
            capture=label["capture"],
        )

    return data_segments


def audacity_to_datasegments(
    dcl, capture_name, file_path: str, session: str = "", rate: int = 16000
):
    """Converts labels exported from Audacity into a datasegment object.

    Args:
        dcl (DCLProject): A DCLProject object that is connected to the DCLI file
        capture_name (str): The name of the capture file to import
        file_path (DataFrame): The file path to the Audacity Label
        session (str, optional): The session to set the segments too. Defaults to "".
        rate (int): Audacity uses the actual time and note number of samples. Set the rate to the sample rate for the captured date. Default is 16000.


    Returns:
        Datasegment
    """

    M = []
    with open(file_path, "r") as fid:
        for line in fid.readlines():
            if line[0] == "\\":
                continue
            start, end, label = line[:-1].split("\t")
            M.append([float(start), float(end), label])

    tmp_df = DataFrame(
        M,
        columns=[
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "label_value",
        ],
    )

    tmp_df["capture_sample_sequence_start"] = (
        tmp_df["capture_sample_sequence_start"] * rate
    ).astype(int)
    tmp_df["capture_sample_sequence_end"] = (
        tmp_df["capture_sample_sequence_end"] * rate
    ).astype(int)

    tmp_df["capture"] = capture_name
    tmp_df["session"] = session

    return segment_list_to_datasegments(dcl, tmp_df)


def check_overlap(s1, s2):
    return (
        True
        if max(
            0,
            min(s1["capture_sample_sequence_end"], s2["capture_sample_sequence_end"])
            - max(
                s1["capture_sample_sequence_start"], s2["capture_sample_sequence_start"]
            ),
        )
        > 0
        else False
    )


def check_near(s1, s2, delta):
    if delta is None:
        return True

    return (
        True
        if abs(s2["capture_sample_sequence_start"] - s1["capture_sample_sequence_end"])
        < delta
        else False
    )


def template(segment, min_length=1, start=None, end=None):
    if start is None:
        start = segment["capture_sample_sequence_start"]
    if end is None:
        end = segment["capture_sample_sequence_end"]

    difference = end - start
    if difference < min_length:
        end += int(min_length - difference) // 2
        start -= int(min_length - difference) // 2
    if start < 0:
        print("Error: Start of a segment was less than 0")
        start = 0

    return {
        "capture_sample_sequence_start": start,
        "capture_sample_sequence_end": end,
        "label_value": segment["label_value"],
        "length": end - start,
        "capture": segment["capture"],
        "session": segment["session"],
    }


def merge_segments(segments: DataFrame, delta: int = 10) -> DataFrame:
    """Merges data segments that are within a distance delta of each other and have the same class name.

    Args:
        segments (DataFrame): A DataFrame of segments
        delta (int, optional): The distance between two nonoverlapping segments where they will still be merged. Defaults to 10.

    Returns:
        DataFrame: DataFrame containing the merged segments
    """

    if isinstance(segments, DataFrame):
        seg_groups = segments.groupby(["session", "capture"])

    elif isinstance(segments, DataSegments):
        seg_groups = segments.to_dataframe().groupby(["session", "capture"])

    else:
        raise Exception("Expected DataFrame or DataSegments")

    for key in seg_groups.groups.keys():

        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .to_dict(orient="records")
        )

        merge_list = []
        new_segments = []

        for index, segment in enumerate(segment_list):

            if not merge_list:
                if len(segment_list) - 1 == index:
                    new_segments.append(template(segment))
                    # print('ending')
                    continue
                elif segment_list[index + 1]["label_value"] != segment["label_value"]:
                    new_segments.append(template(segment))
                    # print('no merge list diff value', index)
                    continue
                elif not check_near(
                    segment, segment_list[index + 1], delta
                ) and not check_overlap(segment, segment_list[index + 1]):
                    new_segments.append(template(segment))
                    # print('no merge list to large', index)
                    # print("no merge list", check_overlap(segment, segment_list[index+1]))
                    continue

            if (
                len(segment_list) - 1 != index
                and segment_list[index + 1]["label_value"] == segment["label_value"]
                and (
                    check_near(segment, segment_list[index + 1], delta)
                    or check_overlap(segment, segment_list[index + 1])
                )
            ):

                if not merge_list:
                    # print("add merge list", index)
                    merge_list.append(index)
                merge_list.append(index + 1)

            else:
                # do merge
                if merge_list:
                    new_segments.append(
                        template(
                            segment_list[merge_list[0]],
                            start=segment_list[merge_list[0]][
                                "capture_sample_sequence_start"
                            ],
                            end=segment_list[merge_list[-1]][
                                "capture_sample_sequence_end"
                            ],
                        )
                    )
                else:
                    new_segments.append(template(segment))

                merge_list = []

        if merge_list:
            new_segments.append(
                template(
                    segment_list[merge_list[0]],
                    start=segment_list[merge_list[0]]["capture_sample_sequence_start"],
                    end=segment_list[merge_list[-1]]["capture_sample_sequence_end"],
                )
            )

    print("Original Segments:", len(segments), "Merged Segments:", len(new_segments))

    return DataFrame(new_segments)


def filter_segments(segments, min_length=10000) -> DataFrame:
    """Merges data segments that are within a distance delta of each other and have the same class name."""

    if isinstance(segments, DataFrame):
        seg_groups = segments.groupby(["session", "capture"])

    elif isinstance(segments, DataSegments):
        seg_groups = segments.to_dataframe().groupby(["session", "capture"])

    else:
        raise Exception("Expected DataFrame or DataSegments")

    for key in seg_groups.groups.keys():

        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .to_dict(orient="records")
        )

        new_segments = []

        for _, segment in enumerate(segment_list):
            if segment["length"] > min_length:
                new_segments.append(template(segment))

    print("Original Segments:", len(segments), "Filtered Segments:", len(new_segments))

    return DataFrame(new_segments)


def remove_overlap(segments) -> DataFrame:
    """Removes the overlap between segments by setting the segment start and end of
    overlapping segments to the same point, halfway between the overlapping edges."""

    if isinstance(segments, DataFrame):
        seg_groups = segments.groupby(["session", "capture"])

    elif isinstance(segments, DataSegments):
        seg_groups = segments.to_dataframe().groupby(["session", "capture"])

    else:
        raise Exception("Expected DataFrame or DataSegments")

    for key in seg_groups.groups.keys():

        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .to_dict(orient="records")
        )

        new_segments = []

        for index in range(len(segment_list[:-1])):
            if check_overlap(segment_list[index], segment_list[index + 1]):
                difference = (
                    abs(
                        (
                            segment_list[index + 1]["capture_sample_sequence_start"]
                            - segment_list[index]["capture_sample_sequence_end"]
                        )
                    )
                    + 1
                ) // 2
                segment_list[index]["capture_sample_sequence_end"] -= difference
                segment_list[index + 1]["capture_sample_sequence_start"] += difference

        new_segments.extend(segment_list)

    tmp_df = DataFrame(new_segments)
    tmp_df.length = (
        tmp_df.capture_sample_sequence_end - tmp_df.capture_sample_sequence_start
    )

    return tmp_df


def join_segments(segments, delta: Optional[int] = None) -> DataFrame:
    """If there are any gaps between two segments, this will bring them together so there are no unlabeled regions of data."""

    if isinstance(segments, DataFrame):
        seg_groups = segments.groupby(["session", "capture"])

    elif isinstance(segments, DataSegments):
        seg_groups = segments.to_dataframe().groupby(["session", "capture"])

    else:
        raise Exception("Expected DataFrame or DataSegments")

    for key in seg_groups.groups.keys():

        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .to_dict(orient="records")
        )

        new_segments = []

        for index in range(len(segment_list[:-1])):
            if (
                not check_overlap(segment_list[index], segment_list[index + 1]) and True
                if delta is None
                else check_near(
                    segment_list[index], segment_list[index + 1], delta=delta
                )
            ):
                difference = (
                    abs(
                        (
                            segment_list[index + 1]["capture_sample_sequence_start"]
                            - segment_list[index]["capture_sample_sequence_end"]
                        )
                    )
                    + 1
                ) // 2
                segment_list[index]["capture_sample_sequence_end"] += difference
                segment_list[index + 1]["capture_sample_sequence_start"] -= difference

        new_segments.extend(segment_list)

    tmp_df = DataFrame(new_segments)
    tmp_df.length = (
        tmp_df.capture_sample_sequence_end - tmp_df.capture_sample_sequence_start
    )

    return tmp_df
