"""LangGraph stock analysis agent for Jupyter Notebook use.

This module builds a small LangGraph workflow that:
- fetches 60 days of daily price data with yfinance
- computes SMA-10, SMA-20, and RSI-14 with pandas
- produces a strict BUY / HOLD / SELL recommendation
- formats a markdown-style report

Install dependencies:
    pip install yfinance langgraph langchain-core pandas

Notebook usage:
    from stock_market_langgraph_agent import create_stock_graph, run_stock_analysis
    graph = create_stock_graph()
    result = graph.invoke({"ticker": "AAPL"})
    print(result["report"])
"""

from __future__ import annotations

from typing import TypedDict, Dict, Any

import pandas as pd
import yfinance as yf
from langgraph.graph import StateGraph, START, END


class StockState(TypedDict, total=False):
    """Shared graph state passed between nodes."""

    ticker: str
    historical_data: pd.DataFrame
    indicators: Dict[str, float]
    recommendation: str
    report: str
    errors: str


def fetch_data_node(state: StockState) -> StockState:
    """Fetch exactly 60 days of daily historical data for the requested ticker."""
    ticker = (state.get("ticker") or "").strip().upper()

    if not ticker:
        return {
            "ticker": ticker,
            "historical_data": pd.DataFrame(),
            "errors": "Ticker symbol is empty.",
        }

    try:
        data = yf.download(
            ticker,
            period="60d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False,
        )

        if data is None or data.empty:
            return {
                "ticker": ticker,
                "historical_data": pd.DataFrame(),
                "errors": f"No historical data returned for ticker '{ticker}'.",
            }

        if "Close" not in data.columns:
            return {
                "ticker": ticker,
                "historical_data": pd.DataFrame(),
                "errors": f"Fetched data for '{ticker}' does not contain a Close column.",
            }

        data = data.copy()
        data.index = pd.to_datetime(data.index)

        return {
            "ticker": ticker,
            "historical_data": data,
            "errors": "",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ticker": ticker,
            "historical_data": pd.DataFrame(),
            "errors": f"Data fetch failed for '{ticker}': {exc}",
        }


def _extract_close_series(data: pd.DataFrame) -> pd.Series:
    """Return a 1-D close series from yfinance output.

    yfinance may return either:
    - a normal single-index DataFrame with a Close column
    - a multi-index DataFrame where Close is itself a DataFrame
    """
    close_data = data["Close"]

    if isinstance(close_data, pd.DataFrame):
        if close_data.shape[1] == 1:
            close_data = close_data.iloc[:, 0]
        else:
            close_data = close_data.bfill(axis=1).iloc[:, 0]

    if not isinstance(close_data, pd.Series):
        close_data = pd.Series(close_data)

    return pd.to_numeric(close_data, errors="coerce").dropna()


def calculate_indicators_node(state: StockState) -> StockState:
    """Compute SMA-10, SMA-20, and RSI-14 using pandas only."""
    data = state.get("historical_data", pd.DataFrame())

    if data.empty or "Close" not in data.columns:
        return {
            "indicators": {},
            "errors": state.get("errors", "") or "No valid price data available for indicator calculation.",
        }

    try:
        close = _extract_close_series(data)
    except Exception as exc:  # noqa: BLE001
        return {
            "indicators": {},
            "errors": state.get("errors", "") or f"Failed to normalize close prices: {exc}",
        }

    if close.empty:
        return {
            "indicators": {},
            "errors": state.get("errors", "") or "Close series is empty after numeric coercion.",
        }

    sma_10 = close.rolling(window=10, min_periods=10).mean().iloc[-1]
    sma_20 = close.rolling(window=20, min_periods=20).mean().iloc[-1]

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    rsi_value = rsi.iloc[-1]

    indicators = {
        "sma_10": float(sma_10) if pd.notna(sma_10) else float("nan"),
        "sma_20": float(sma_20) if pd.notna(sma_20) else float("nan"),
        "rsi_14": float(rsi_value) if pd.notna(rsi_value) else float("nan"),
        "latest_close": float(close.iloc[-1]),
    }

    return {
        "indicators": indicators,
        "errors": state.get("errors", ""),
    }


def recommendation_node(state: StockState) -> StockState:
    """Apply the strict rule-based trading logic."""
    indicators = state.get("indicators", {})
    sma_10 = indicators.get("sma_10")
    sma_20 = indicators.get("sma_20")
    rsi_14 = indicators.get("rsi_14")

    if any(value is None or pd.isna(value) for value in [sma_10, sma_20, rsi_14]):
        return {
            "recommendation": "HOLD",
            "errors": state.get("errors", "") or "Insufficient indicator values to generate a recommendation.",
        }

    if sma_10 > sma_20 and 30 <= rsi_14 <= 70:
        recommendation = "BUY"
    elif sma_10 < sma_20 or rsi_14 > 70:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return {
        "recommendation": recommendation,
        "errors": state.get("errors", ""),
    }


def format_report_node(state: StockState) -> StockState:
    """Compile the final markdown-style report."""
    ticker = state.get("ticker", "UNKNOWN")
    indicators = state.get("indicators", {})
    recommendation = state.get("recommendation") or "N/A"
    errors = state.get("errors", "")

    latest_close = indicators.get("latest_close")
    sma_10 = indicators.get("sma_10")
    sma_20 = indicators.get("sma_20")
    rsi_14 = indicators.get("rsi_14")

    def fmt(value: Any) -> str:
        return "N/A" if value is None or pd.isna(value) else f"{value:.2f}"

    report_lines = [
        f"# Stock Analysis Report: {ticker}",
        "",
        f"- **Ticker Symbol:** {ticker}",
        f"- **Current Price:** {fmt(latest_close)}",
        f"- **SMA-10:** {fmt(sma_10)}",
        f"- **SMA-20:** {fmt(sma_20)}",
        f"- **RSI-14:** {fmt(rsi_14)}",
        f"- **Recommendation:** {recommendation}",
        f"- **Errors:** {errors if errors else 'None'}",
    ]

    return {
        "report": "\n".join(report_lines),
    }


def route_after_fetch(state: StockState) -> str:
    """Route to END when fetch fails, otherwise continue the graph."""
    return "format_report" if state.get("errors") else "calculate_indicators"


def create_stock_graph():
    """Build and compile the LangGraph workflow."""
    graph = StateGraph(StockState)

    graph.add_node("fetch_data", fetch_data_node)
    graph.add_node("calculate_indicators", calculate_indicators_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("format_report", format_report_node)

    graph.add_edge(START, "fetch_data")
    graph.add_conditional_edges("fetch_data", route_after_fetch, {
        "calculate_indicators": "calculate_indicators",
        "format_report": "format_report",
    })
    graph.add_edge("calculate_indicators", "recommendation")
    graph.add_edge("recommendation", "format_report")
    graph.add_edge("format_report", END)

    return graph.compile()


def run_stock_analysis(ticker: str) -> StockState:
    """Convenience wrapper for notebook execution."""
    app = create_stock_graph()
    return app.invoke(
        {
            "ticker": ticker,
            "historical_data": pd.DataFrame(),
            "indicators": {},
            "recommendation": "",
            "report": "",
            "errors": "",
        }
    )


if __name__ == "__main__":
    T= input("Enter valid Ticker: ")
    if (not T):
        print("\n=== Failing ticker: INVALID_TICKER ===")
        failing_result = run_stock_analysis("INVALID_TICKER")
        print(failing_result["report"])
    else:
        print(f"=== Successful ticker: {T} ===")
        success_result = run_stock_analysis(T)
        print(success_result["report"])


