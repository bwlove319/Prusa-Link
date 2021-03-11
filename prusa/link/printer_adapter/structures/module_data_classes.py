"""
Decided that keeping module data externally will aid with gathering them for
the api, definitions of which is what this module contains
"""
from typing import Deque, Optional, Set, List, Any, Dict

from pydantic import BaseModel

from prusa.connect.printer.const import State

from .model_classes import JobState, SDState


class FilePrinterData(BaseModel):
    """Data of the FilePrinter class"""
    tmp_file_path: Optional[str]
    pp_file_path: Optional[str]
    printing: Optional[bool]
    stopped_forcefully: Optional[bool]
    paused: Optional[bool]
    line_number: Optional[int]
    enqueued: Optional[Deque]
    gcode_number: Optional[int]


class StateManagerData(BaseModel):
    """Data of the StateManager class"""
    # The ACTUAL states considered when reporting
    base_state: Optional[State] = State.READY
    printing_state: Optional[State] = None
    override_state: Optional[State] = None

    # Reported state history
    last_state: Optional[State]
    current_state: Optional[State]
    state_history: Optional[Deque[State]]
    error_count: Optional[int]


class JobData(BaseModel):
    """Data of the Job class"""
    job_start_cmd_id: Optional[int]
    printing_file_path: Optional[str]
    printing_file_m_time: Optional[str]
    printing_file_size: Optional[str]
    printing_file_byte: Optional[int]
    filename_only: Optional[bool]
    from_sd: Optional[bool]
    inbuilt_reporting: Optional[bool]

    job_id: Optional[int]
    job_state: Optional[JobState]

    def get_job_id_for_api(self):
        """
        The API does not send None values. This function returns None when
        no job is running, otherwise it gives the job_id
        """
        if self.job_state == JobState.IDLE:
            return None
        return self.job_id


class IpUpdaterData(BaseModel):
    """Data of the IpUpdater class"""
    local_ip: Optional[str]
    update_ip_on: Optional[float]


class SDCardData(BaseModel):
    """Data of the SDCard class"""
    expecting_insertion: Optional[bool]
    invalidated: Optional[bool]
    is_flash_air: Optional[bool]
    last_updated: Optional[float]
    last_checked_flash_air: Optional[float]
    sd_state: Optional[SDState]
    files: Optional[Any]  # We cannot type-check SDFile, only basic ones
    sfn_to_lfn_paths: Optional[Dict[str, str]]
    lfn_to_sfn_paths: Optional[Dict[str, str]]
    mixed_to_lfn_paths: Optional[Dict[str, str]]


class MountsData(BaseModel):
    """Data of the Mounts class"""
    blacklisted_paths: Optional[List[str]]
    blacklisted_names: Optional[List[str]]
    configured_mounts: Optional[Set[str]]
    mounted_set: Optional[Set[str]]


class PrintStatsData(BaseModel):
    """Data of the PrintStats class"""
    print_time: Optional[float]
    segment_start: Optional[float]
    has_inbuilt_stats: Optional[bool]
    total_gcode_count: Optional[int]
