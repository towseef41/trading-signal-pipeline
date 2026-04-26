"""
Reporting endpoints.
"""

from fastapi import APIRouter, Depends

from trading_signal_pipeline.interfaces.api.v1.dependencies import get_generate_report_service
from trading_signal_pipeline.interfaces.api.v1.auth import require_api_key
from trading_signal_pipeline.application.generate_report import GenerateReportService
from trading_signal_pipeline.interfaces.api.v1.schemas import ApiResponse, ErrorResponse, ReportOut
from trading_signal_pipeline.interfaces.api.v1.constants import PREFIX_REPORT

router = APIRouter(prefix=PREFIX_REPORT)


@router.get(
    "/",
    response_model=ApiResponse[ReportOut],
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def get_report(
    _auth: None = Depends(require_api_key),
    service: GenerateReportService = Depends(get_generate_report_service),
):
    """
    Generate a report from stored signals and the latest backtest result.

    Returns:
        JSON report dictionary.
    """
    report = service.generate()
    return ApiResponse[ReportOut](data=report)
