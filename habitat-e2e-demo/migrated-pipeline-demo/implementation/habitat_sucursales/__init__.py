"""Portable Sucursales transformations and mock pipeline orchestration."""

from .periods import ProcessingPeriods, calculate_periods
from .pipeline import (
    PipelineExecutionError,
    process_agendamientos,
    process_atenciones,
    run_pipeline,
)
from .transformations import (
    transform_agendamientos_base,
    transform_agendamientos_motivos,
    transform_atenciones_base,
    transform_atenciones_motivos,
)

__all__ = [
    "PipelineExecutionError",
    "ProcessingPeriods",
    "calculate_periods",
    "process_agendamientos",
    "process_atenciones",
    "run_pipeline",
    "transform_agendamientos_base",
    "transform_agendamientos_motivos",
    "transform_atenciones_base",
    "transform_atenciones_motivos",
]
