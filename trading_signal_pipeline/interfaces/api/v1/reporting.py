"""
Reporting endpoints.
"""

from fastapi import APIRouter, Depends

from trading_signal_pipeline.interfaces.api.v1.dependencies import get_generate_report_service
from trading_signal_pipeline.interfaces.api.v1.auth import require_api_key
from trading_signal_pipeline.application.generate_report import GenerateReportService

router = APIRouter(prefix="/v1/report")


@router.get("/")
def get_report(
    _auth: None = Depends(require_api_key),
    service: GenerateReportService = Depends(get_generate_report_service),
):
    """
    Generate a report from stored signals and the latest backtest result.

    Returns:
        JSON report dictionary.
    """
    return service.generate()
