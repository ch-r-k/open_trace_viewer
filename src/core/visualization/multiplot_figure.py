from plotly.subplots import make_subplots
import plotly.graph_objects as go


class MultiPlotFigure:
    """Builds a vertical stack of subplots and places traces/annotations in correct rows."""

    def __init__(self, shared_xaxes=True, title="Time Series Overview"):
        self.title = title
        self.shared_xaxes = shared_xaxes
        self._registered = []  # list of dicts: {type, data, title}

    def add_metric_subplot(self, title: str, df, x_col="x", y_col="y", plot_type="line"):
        """Register a metric subplot. df must contain x_col and y_col."""
        self._registered.append({
            "kind": "metric",
            "title": title,
            "data": df,
            "x_col": x_col,
            "y_col": y_col,
            "plot_type": plot_type
        })

    def add_timeline_subplot(self, title: str, traces, annotations):
        """Register the timeline subplot; traces should be list of go.Traces."""
        self._registered.append({
            "kind": "timeline",
            "title": title,
            "traces": traces,
            "annotations": annotations
        })

    def build_figure(self):
        n_rows = len(self._registered)
        if n_rows == 0:
            raise ValueError("No subplots registered.")

        specs = [[{"type": "xy"}] for _ in range(n_rows)]
        titles = [r["title"] for r in self._registered]

        fig = make_subplots(
            rows=n_rows,
            cols=1,
            shared_xaxes=self.shared_xaxes,
            subplot_titles=titles,
            specs=specs
        )

        for idx, reg in enumerate(self._registered, start=1):
            if reg["kind"] == "metric":
                df = reg["data"]
                x = df[reg["x_col"]]
                y = df[reg["y_col"]]
                ptype = reg["plot_type"]

                # Default hover text to show state if available
                hover_text = df.get("State") if "State" in df.columns else y

                if ptype == "area":
                    trace = go.Scatter(
                        x=x,
                        y=y,
                        mode="lines",
                        name=reg["title"],
                        fill="tozeroy"
                    )
                elif ptype == "step":
                    # Step-style line using categorical y-axis
                    trace = go.Scatter(
                        x=x,
                        y=df["State"],  # use actual state names for y
                        mode="lines+markers",
                        name=reg["title"],
                        line=dict(shape="hv", width=2),
                        hoverinfo="x+y+name"
                    )

                    # Force y-axis to be categorical with all states in order
                    fig.update_yaxes(
                        categoryorder="array",
                        categoryarray=list(df["State"].unique()),
                        title_text=reg["title"],
                        row=idx,
                        col=1
                    )
                elif ptype == "scatter":
                    trace = go.Scatter(
                        x=x,
                        y=y,
                        mode="markers",
                        name=reg["title"]
                    )
                elif ptype == "bar":
                    trace = go.Bar(x=x, y=y, name=reg["title"])
                else:
                    # Fallback to simple line
                    trace = go.Scatter(
                        x=x,
                        y=y,
                        mode="lines",
                        name=reg["title"]
                    )

                fig.add_trace(trace, row=idx, col=1)

                # Simple y-axis title
                fig.update_yaxes(title_text=reg["title"], row=idx, col=1)

            elif reg["kind"] == "timeline":
                # Add all traces (they were created with generic axis references)
                for t in reg["traces"]:
                    fig.add_trace(t, row=idx, col=1)

                # Timeline-specific layout
                fig.update_yaxes(title_text="Tasks", row=idx, col=1)
                fig.update_xaxes(title_text="Time (s)", row=idx, col=1)

                # Attach annotations if any
                if reg.get("annotations"):
                    existing = list(fig.layout.annotations) if fig.layout.annotations else []
                    fig.update_layout(annotations=existing + reg["annotations"])

        # Global layout
        fig.update_layout(
            title=self.title,
            height=300 * n_rows,
            margin=dict(t=80, l=120),
            barmode="overlay",
            dragmode="zoom",
            yaxis_fixedrange=True
        )

        return fig
