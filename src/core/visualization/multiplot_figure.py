# core/visualization/multiplot_figure.py
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
                if reg["plot_type"] in ("line", "area"):
                    fig.add_trace(
                        go.Scatter(x=x, y=y, mode="lines", name=reg["title"], fill="tozeroy" if reg["plot_type"] == "area" else None),
                        row=idx, col=1
                    )
                elif reg["plot_type"] == "scatter":
                    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name=reg["title"]), row=idx, col=1)
                elif reg["plot_type"] == "bar":
                    fig.add_trace(go.Bar(x=x, y=y, name=reg["title"]), row=idx, col=1)
                else:
                    # fallback to line
                    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=reg["title"]), row=idx, col=1)

                # simple y-axis title
                fig.update_yaxes(title_text=reg["title"], row=idx, col=1)

            elif reg["kind"] == "timeline":
                # add all traces (they were created with generic axis references)
                for t in reg["traces"]:
                    fig.add_trace(t, row=idx, col=1)

                # timeline-specific layout
                # force categorical order for y if possible
                # leave y-axis title to "Tasks"
                fig.update_yaxes(title_text="Tasks", row=idx, col=1)
                fig.update_xaxes(title_text="Time (s)", row=idx, col=1)

                # attach annotations — they already have xref/yref like "xN"/"yN" computed with timeline row
                if reg.get("annotations"):
                    # append to existing annotations if any
                    existing = list(fig.layout.annotations) if fig.layout.annotations else []
                    fig.update_layout(annotations=existing + reg["annotations"])

        # global layout
        fig.update_layout(
            title=self.title,
            height=300 * n_rows,
            margin=dict(t=80, l=120),
            barmode="overlay",
            dragmode="zoom",
            yaxis_fixedrange=True
        )
        return fig
