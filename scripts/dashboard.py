import streamlit as st
import pandas as pd
import yaml
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"

st.set_page_config(page_title="Day 13 AI Observability", layout="wide")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["dashboard"]

def load_data(source_path):
    full_path = REPO_ROOT / source_path
    if not full_path.exists():
        return None
    data = []
    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if "ts" in df.columns:
        df["timestamp"] = pd.to_datetime(df["ts"])
    elif "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

config = load_config()
st.title(config.get("title", "Dashboard"))

# Refresh logic (manual or simple rerun)
col_timer, col_refresh = st.columns([8, 1])
with col_refresh:
    if st.button("Refresh"):
        st.rerun()

st.write(f"**Time Range:** Last {config.get('time_range_minutes', 60)} minutes")

df = load_data("data/logs.jsonl")

if df is None:
    st.warning("File `data/logs.jsonl` chưa tồn tại. Vui lòng hoàn thành Checkpoint 1 hoặc chạy API/load_test để sinh file này.")
    st.stop()
elif df.empty:
    st.info("File `data/logs.jsonl` trống. Đang chờ dữ liệu...")
    st.stop()

# Ensure timestamp exists
if "timestamp" not in df.columns:
    st.error("Log data không có trường 'timestamp'.")
    st.stop()

# Filter by time range
min_time = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=config.get("time_range_minutes", 60))
# Assuming timestamps in logs might be naive or UTC, let's normalize
if df["timestamp"].dt.tz is None:
    min_time = min_time.tz_localize(None)
else:
    min_time = min_time.tz_convert(df["timestamp"].dt.tz)

df_filtered = df[df["timestamp"] >= min_time].copy()

if df_filtered.empty:
    st.info("Không có dữ liệu trong khoảng thời gian đã chọn.")
    st.stop()

# Helpers for plotting
def plot_time_series(df_sub, time_col, val_col, agg, threshold_val=None, title="", ylabel=""):
    if df_sub.empty:
        return go.Figure()
    df_sub = df_sub.set_index(time_col)
    if agg == "sum":
        resampled = df_sub[val_col].resample("1min").sum().reset_index()
    elif agg == "count":
        resampled = df_sub[val_col].resample("1min").count().reset_index()
    else:
        resampled = df_sub[val_col].resample("1min").mean().reset_index()
    
    fig = px.line(resampled, x=time_col, y=val_col, title=title)
    fig.update_layout(yaxis_title=ylabel, xaxis_title="Time")
    
    if threshold_val is not None:
        fig.add_hline(y=threshold_val, line_dash="dash", line_color="red", annotation_text="Threshold")
    return fig

# Render Panels
panels = config.get("panels", [])

col1, col2 = st.columns(2)

for i, panel in enumerate(panels):
    pid = panel.get("id")
    ptitle = panel.get("title")
    events = panel.get("events", [])
    threshold_val = panel.get("threshold", {}).get("value")
    threshold_op = panel.get("threshold", {}).get("operator")
    
    df_panel = df_filtered[df_filtered["event"].isin(events)].copy()
    
    with (col1 if i % 2 == 0 else col2):
        st.subheader(ptitle)
        
        if df_panel.empty:
            st.write("Chưa có dữ liệu cho panel này.")
            continue
            
        if pid == "latency":
            # P50, P95, P99
            if "latency_ms" in df_panel.columns:
                p50 = df_panel["latency_ms"].quantile(0.50)
                p95 = df_panel["latency_ms"].quantile(0.95)
                p99 = df_panel["latency_ms"].quantile(0.99)
                
                m1, m2, m3 = st.columns(3)
                color95 = "inverse" if threshold_op == "lte" and p95 > threshold_val else "normal"
                m1.metric("P50 (ms)", f"{p50:.1f}")
                m2.metric("P95 (ms)", f"{p95:.1f}", delta=f"Thresh: {threshold_val}", delta_color=color95)
                m3.metric("P99 (ms)", f"{p99:.1f}")
                
                # Chart
                fig = plot_time_series(df_panel, "timestamp", "latency_ms", "mean", threshold_val, "Latency (avg per min)", "ms")
                st.plotly_chart(fig, use_container_width=True)
                
        elif pid == "traffic":
            rate = len(df_panel) / config.get("time_range_minutes", 60)
            color = "inverse" if threshold_op == "gte" and rate < threshold_val else "normal"
            st.metric("Avg Request/min", f"{rate:.2f}", delta=f"Thresh: {threshold_val}", delta_color=color)
            
            # Chart
            df_panel["count"] = 1
            fig = plot_time_series(df_panel, "timestamp", "count", "count", None, "Requests per minute", "count")
            st.plotly_chart(fig, use_container_width=True)
            
        elif pid == "errors":
            req_rcv = len(df_filtered[df_filtered["event"] == "request_received"])
            req_fail = len(df_filtered[df_filtered["event"] == "request_failed"])
            err_rate = (req_fail / req_rcv * 100) if req_rcv > 0 else 0
            
            color = "inverse" if threshold_op == "lte" and err_rate > threshold_val else "normal"
            st.metric("Error Rate (%)", f"{err_rate:.2f}%", delta=f"Thresh: {threshold_val}", delta_color=color)
            
            df_err = df_filtered[df_filtered["event"] == "request_failed"]
            if not df_err.empty and "error_type" in df_err.columns:
                err_counts = df_err["error_type"].value_counts().reset_index()
                err_counts.columns = ["error_type", "count"]
                fig = px.pie(err_counts, names="error_type", values="count", title="Error Breakdown")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Không có lỗi.")
                
        elif pid == "cost":
            if "cost_usd" in df_panel.columns:
                total_cost = df_panel["cost_usd"].sum()
                color = "inverse" if threshold_op == "lte" and total_cost > threshold_val else "normal"
                st.metric("Total Cost (USD)", f"${total_cost:.4f}", delta=f"Thresh: {threshold_val}", delta_color=color)
                
                fig = plot_time_series(df_panel, "timestamp", "cost_usd", "sum", None, "Cost per minute", "USD")
                st.plotly_chart(fig, use_container_width=True)
                
        elif pid == "tokens":
            if "tokens_in" in df_panel.columns and "tokens_out" in df_panel.columns:
                total_in = df_panel["tokens_in"].sum()
                total_out = df_panel["tokens_out"].sum()
                total_tokens = total_in + total_out
                
                color = "inverse" if threshold_op == "lte" and total_tokens > threshold_val else "normal"
                st.metric("Total Tokens", f"{total_tokens:,.0f}", delta=f"Thresh: {threshold_val}", delta_color=color)
                
                fig = go.Figure(data=[
                    go.Bar(name='Tokens In', x=['Tokens'], y=[total_in]),
                    go.Bar(name='Tokens Out', x=['Tokens'], y=[total_out])
                ])
                fig.update_layout(barmode='stack', title="Tokens Breakdown")
                st.plotly_chart(fig, use_container_width=True)
                
        elif pid == "quality":
            if "quality_score" in df_panel.columns:
                mean_q = df_panel["quality_score"].mean()
                color = "inverse" if threshold_op == "gte" and mean_q < threshold_val else "normal"
                st.metric("Mean Quality Score", f"{mean_q:.2f}", delta=f"Thresh: {threshold_val}", delta_color=color)
                
                fig = plot_time_series(df_panel, "timestamp", "quality_score", "mean", threshold_val, "Quality Score over time", "Score")
                st.plotly_chart(fig, use_container_width=True)
