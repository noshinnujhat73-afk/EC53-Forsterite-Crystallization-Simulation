from __future__ import annotations

import io
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.model import EA_OVER_K_K, NU_S_INV, integrate_crystallinity

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE = BASE_DIR / "input" / "ec53_temperature_history.csv"

st.set_page_config(
    page_title="EC 53 Forsterite Crystallization Simulator",
    page_icon="🔬",
    layout="wide",
)


def validate_temperature_df(df: pd.DataFrame) -> pd.DataFrame:
    required = {"time_s", "temperature_K"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain exactly these required columns: time_s and temperature_K.")
    out = df[["time_s", "temperature_K"]].copy()
    out["time_s"] = pd.to_numeric(out["time_s"], errors="coerce")
    out["temperature_K"] = pd.to_numeric(out["temperature_K"], errors="coerce")
    if out.isna().any().any():
        raise ValueError("time_s and temperature_K must contain only numeric values.")
    if len(out) < 2:
        raise ValueError("At least two temperature-history rows are required.")
    if (out["temperature_K"] <= 0).any():
        raise ValueError("All temperatures must be greater than 0 K.")
    if (out["time_s"].diff().dropna() <= 0).any():
        raise ValueError("time_s must be strictly increasing.")
    return out


def load_template_if_valid():
    try:
        df = pd.read_csv(TEMPLATE)
        if len(df) >= 2:
            return validate_temperature_df(df)
    except Exception:
        pass
    return None


def result_dataframe(result: dict) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time_s": result["time_s"],
            "time_hr": result["time_s"] / 3600.0,
            "temperature_K": result["temperature_K"],
            "rate_s_inv": result["rate_s_inv"],
            "crystalline_fraction": result["crystalline_fraction"],
            "crystalline_percent": 100.0 * result["crystalline_fraction"],
            "crystalline_fraction_quadrature": result["crystalline_fraction_quadrature"],
            "absolute_validation_error": np.abs(
                result["crystalline_fraction"] - result["crystalline_fraction_quadrature"]
            ),
        }
    )


def make_plot(df: pd.DataFrame, kind: str):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    if kind == "temperature":
        ax.plot(df["time_hr"], df["temperature_K"], linewidth=2)
        ax.set_ylabel("Temperature (K)")
        ax.set_title("Temperature history")
    elif kind == "rate":
        ax.semilogy(df["time_hr"], df["rate_s_inv"], linewidth=2)
        ax.set_ylabel("Crystallization rate k (s⁻¹)")
        ax.set_title("Temperature-dependent crystallization rate")
    else:
        ax.plot(df["time_hr"], df["crystalline_percent"], linewidth=2)
        ax.set_ylabel("Crystalline fraction (%)")
        ax.set_ylim(0, 100)
        ax.set_title("Time-dependent forsterite crystallinity")
    ax.set_xlabel("Time (h)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig


def run_model(df: pd.DataFrame, x0: float, nu: float, ea_over_k: float):
    return integrate_crystallinity(
        df["time_s"].to_numpy(),
        df["temperature_K"].to_numpy(),
        x0=x0,
        nu_s_inv=nu,
        ea_over_k_K=ea_over_k,
    )


def summary(result: dict, x0: float, nu: float, ea_over_k: float):
    rdf = result_dataframe(result)
    return {
        "initial_crystallinity_fraction": float(x0),
        "final_crystallinity_fraction": float(rdf["crystalline_fraction"].iloc[-1]),
        "final_crystallinity_percent": float(rdf["crystalline_percent"].iloc[-1]),
        "maximum_temperature_K": float(rdf["temperature_K"].max()),
        "minimum_temperature_K": float(rdf["temperature_K"].min()),
        "simulation_duration_s": float(rdf["time_s"].iloc[-1] - rdf["time_s"].iloc[0]),
        "simulation_duration_h": float((rdf["time_s"].iloc[-1] - rdf["time_s"].iloc[0]) / 3600.0),
        "maximum_rate_s_inv": float(rdf["rate_s_inv"].max()),
        "nu_s_inv": float(nu),
        "ea_over_k_K": float(ea_over_k),
        "maximum_abs_rk45_vs_quadrature": float(rdf["absolute_validation_error"].max()),
    }


st.title("Time-Dependent Forsterite Crystallization")
st.caption("Protostellar accretion bursts • Non-isothermal kinetics • Source-grounded computational framework")

with st.sidebar:
    st.header("Simulation controls")
    x0_percent = st.number_input("Initial crystallinity (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    st.markdown("**Default kinetic parameters**")
    st.code(f"ν = {NU_S_INV:.3e} s⁻¹\nEa/kB = {EA_OVER_K_K:.0f} K")
    st.caption("These defaults are literature-based in the project documentation; they are not fitted by this app.")
    advanced = st.checkbox("Show advanced parameter controls", value=False)
    if advanced:
        nu = st.number_input("ν (s⁻¹)", min_value=1e5, value=float(NU_S_INV), format="%.4e")
        ea_over_k = st.number_input("Ea/kB (K)", min_value=1.0, value=float(EA_OVER_K_K), format="%.4f")
    else:
        nu, ea_over_k = NU_S_INV, EA_OVER_K_K

    st.divider()
    st.header("Input data")
    uploaded = st.file_uploader("Upload temperature history CSV", type=["csv"])
    use_template = st.button("Load project input CSV")
    st.download_button(
        "Download CSV template",
        data="time_s,temperature_K\n",
        file_name="temperature_history_template.csv",
        mime="text/csv",
    )

if uploaded is not None:
    try:
        input_df = validate_temperature_df(pd.read_csv(uploaded))
        source_label = f"Uploaded file: {uploaded.name}"
        st.session_state["temperature_df"] = input_df
        st.session_state["source_label"] = source_label
    except Exception as exc:
        st.error(str(exc))
        st.stop()
elif use_template:
    template_df = load_template_if_valid()
    if template_df is None:
        st.warning("The project input CSV is intentionally empty until a defensible source/model-derived EC 53 temperature history is supplied.")
    else:
        st.session_state["temperature_df"] = template_df
        st.session_state["source_label"] = "Project input CSV"

input_df = st.session_state.get("temperature_df")
source_label = st.session_state.get("source_label", "No temperature history loaded")

if input_df is None:
    st.warning("No temperature history is loaded. Upload a source/model-derived CSV to enable the simulation.")
    st.info("Required columns: time_s, temperature_K. The app deliberately does not fabricate an EC 53 temperature curve.")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Data points", f"{len(input_df):,}")
    c2.metric("Duration", f"{(input_df.time_s.iloc[-1]-input_df.time_s.iloc[0])/3600:.2f} h")
    c3.metric("Minimum T", f"{input_df.temperature_K.min():.1f} K")
    c4.metric("Maximum T", f"{input_df.temperature_K.max():.1f} K")

    st.subheader("Temperature history")
    preview_fig, preview_ax = plt.subplots(figsize=(10, 3.8))
    preview_ax.plot(input_df.time_s / 3600.0, input_df.temperature_K, linewidth=2)
    preview_ax.set_xlabel("Time (h)")
    preview_ax.set_ylabel("Temperature (K)")
    preview_ax.grid(True, alpha=0.25)
    preview_fig.tight_layout()
    st.pyplot(preview_fig, clear_figure=True)
    plt.close(preview_fig)

    st.caption(source_label)
    with st.expander("Preview input data"):
        st.dataframe(input_df, use_container_width=True, hide_index=True)

    run = st.button("▶ Run simulation", type="primary", use_container_width=True)
    if run:
        try:
            result = run_model(input_df, x0_percent / 100.0, nu, ea_over_k)
            st.session_state["result"] = result
            st.session_state["result_params"] = (x0_percent / 100.0, nu, ea_over_k)
        except Exception as exc:
            st.error(f"Simulation failed: {exc}")

result = st.session_state.get("result")
if result is not None:
    x0_used, nu_used, ea_used = st.session_state["result_params"]
    rdf = result_dataframe(result)
    s = summary(result, x0_used, nu_used, ea_used)

    st.divider()
    st.header("Simulation results")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Final crystallinity", f"{s['final_crystallinity_percent']:.6g} %")
    m2.metric("Maximum temperature", f"{s['maximum_temperature_K']:.6g} K")
    m3.metric("Maximum rate", f"{s['maximum_rate_s_inv']:.3e} s⁻¹")
    m4.metric("Validation max error", f"{s['maximum_abs_rk45_vs_quadrature']:.3e}")

    tabs = st.tabs(["Graphs", "Validation", "Sensitivity", "Data & provenance"])
    with tabs[0]:
        for kind in ("temperature", "rate", "crystallinity"):
            fig = make_plot(rdf, kind)
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)

    with tabs[1]:
        st.subheader("Independent numerical check")
        st.write("The RK45 ODE solution is compared with the independent quadrature solution for the same supplied T(t).")
        st.metric("Maximum absolute difference", f"{s['maximum_abs_rk45_vs_quadrature']:.6e}")
        val = rdf[["time_s", "time_hr", "crystalline_fraction", "crystalline_fraction_quadrature", "absolute_validation_error"]]
        st.dataframe(val, use_container_width=True, hide_index=True)

    with tabs[2]:
        st.subheader("One-factor-at-a-time sensitivity")
        st.caption("Sensitivity values are computational experiments around the selected baseline; they are not observational constraints.")
        temp_factors = st.multiselect("Temperature multiplier", [0.90, 0.95, 1.00, 1.05, 1.10], default=[0.90, 1.00, 1.10])
        nu_factors = st.multiselect("ν multiplier", [0.5, 0.8, 1.0, 1.2, 2.0], default=[0.5, 1.0, 2.0])
        ea_factors = st.multiselect("Ea/kB multiplier", [0.9, 0.95, 1.0, 1.05, 1.1], default=[0.9, 1.0, 1.1])
        rows = []
        for f in temp_factors:
            rr = run_model(input_df.assign(temperature_K=input_df.temperature_K * f), x0_used, nu_used, ea_used)
            rows.append({"analysis": "Temperature", "multiplier": f, "final_crystallinity_percent": 100 * rr["crystalline_fraction"][-1]})
        for f in nu_factors:
            rr = run_model(input_df, x0_used, nu_used * f, ea_used)
            rows.append({"analysis": "ν", "multiplier": f, "final_crystallinity_percent": 100 * rr["crystalline_fraction"][-1]})
        for f in ea_factors:
            rr = run_model(input_df, x0_used, nu_used, ea_used * f)
            rows.append({"analysis": "Ea/kB", "multiplier": f, "final_crystallinity_percent": 100 * rr["crystalline_fraction"][-1]})
        sens = pd.DataFrame(rows)
        st.dataframe(sens, use_container_width=True, hide_index=True)
        for analysis_name in ["Temperature", "ν", "Ea/kB"]:
            sub = sens[sens["analysis"] == analysis_name]
            if not sub.empty:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(sub["multiplier"], sub["final_crystallinity_percent"], marker="o")
                ax.set_xlabel("Multiplier")
                ax.set_ylabel("Final crystallinity (%)")
                ax.set_title(f"Sensitivity to {analysis_name}")
                ax.grid(True, alpha=0.25)
                fig.tight_layout()
                st.pyplot(fig, clear_figure=True)
                plt.close(fig)
        st.download_button("Download sensitivity CSV", sens.to_csv(index=False), "sensitivity_results.csv", "text/csv")

    with tabs[3]:
        st.subheader("Data and provenance")
        st.write(f"**Temperature source:** {source_label}")
        st.write(f"**Initial crystallinity:** {100*x0_used:.6g}%")
        st.write(f"**ν:** {nu_used:.6e} s⁻¹")
        st.write(f"**Ea/kB:** {ea_used:.6g} K")
        st.write("**Rate equation:** k(T) = ν exp[-(Ea/kB)/T]")
        st.write("**Kinetic equation:** dX/dt = k(T)(1 − X)")
        st.write("**Numerical solver:** SciPy RK45")
        st.info("The application distinguishes source-derived input, literature-based kinetic parameters, numerical settings, and derived outputs. A result is not an EC 53 observational measurement.")

    csv_bytes = rdf.to_csv(index=False).encode("utf-8")
    json_bytes = json.dumps(s, indent=2).encode("utf-8")
    st.download_button("Download simulation CSV", csv_bytes, "baseline_timeseries.csv", "text/csv")
    st.download_button("Download summary JSON", json_bytes, "baseline_summary.json", "application/json")
