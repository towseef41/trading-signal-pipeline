"""
Built-in report sections.
"""

from trading_signal_pipeline.ports.report_section import ReportSection
from trading_signal_pipeline.serialization.primitives import trade_to_dict


class PerformanceSection(ReportSection):
    """Section that returns the computed metrics."""

    def name(self) -> str:
        """See base class."""
        return "performance"

    def generate(self, metrics, trades, signals):
        """See base class."""
        return metrics


class TradesSection(ReportSection):
    """Section summarizing completed trades."""

    def name(self) -> str:
        """See base class."""
        return "trades_summary"

    def generate(self, metrics, trades, signals):
        """See base class."""
        return {
            "total_trades": len(trades),
            "last_trade": trade_to_dict(trades[-1]) if trades else None,
        }


class SignalsSection(ReportSection):
    """Section summarizing ingested signals."""

    def name(self) -> str:
        """See base class."""
        return "signals_summary"

    def generate(self, metrics, trades, signals):
        """See base class."""
        return {
            "total_signals": len(signals),
            "last_signal": signals[-1] if signals else None,
        }
