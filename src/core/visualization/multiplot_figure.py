from plotly.subplots import make_subplots
import plotly.graph_objects as go


class MultiPlotFigure:
    """Builds a horizontal row of subplots and places traces/annotations in correct cols."""

    def __init__(self, shared_yaxes=True, title="Time Series Overview"):
        self.title = title
        self.shared_yaxes = shared_yaxes
        self._registered = []  # list of dicts: {type, data, title}

    def add_metric_subplot(self, title: str, df, x_col="x", y_col="y", plot_type="line"):
        self._registered.append({
            "kind": "metric",
            "title": title,
            "data": df,
            "x_col": x_col,
            "y_col": y_col,
            "plot_type": plot_type
        })

    def add_notes_subplot(self, title: str, traces, annotations):
        self._registered.append({
            "kind": "notes",
            "title": title,
            "traces": traces,
            "annotations": annotations
        })

    def add_timeline_subplot(self, title: str, traces, annotations):
        self._registered.append({
            "kind": "timeline",
            "title": title,
            "traces": traces,
            "annotations": annotations
        })

    def build_figure(self):
        n_cols = len(self._registered)
        if n_cols == 0:
            raise ValueError("No subplots registered.")

        specs = [[{"type": "xy"} for _ in range(n_cols)]]
        titles = [r["title"] for r in self._registered]

        fig = make_subplots(
            rows=1,
            cols=n_cols,
            shared_yaxes=self.shared_yaxes,
            subplot_titles=titles,
            specs=specs
        )

        for idx, reg in enumerate(self._registered, start=1):
            if reg["kind"] == "metric":
                df = reg["data"]
                x = df[reg["x_col"]]
                y = df[reg["y_col"]]
                ptype = reg["plot_type"]

                # flip x/y to make vertical plots
                if ptype == "area":
                    trace = go.Scatter(
                        x=y,
                        y=x,
                        mode="lines",
                        name=reg["title"],
                        fill="tozeroy"
                    )

                elif ptype == "step":
                    trace = go.Scatter(
                        x=df["State"],
                        y=x,
                        mode="lines+markers",
                        name=reg["title"],
                        line=dict(shape="vh", width=2),
                    )
                    fig.update_xaxes(
                        categoryorder="array",
                        categoryarray=list(df["State"].unique()),
                        row=1, col=idx
                    )

                elif ptype == "scatter":
                    trace = go.Scatter(x=y, y=x, mode="markers", name=reg["title"])

                elif ptype == "bar":
                    trace = go.Bar(x=y, y=x, name=reg["title"], orientation="v")

                else:
                    trace = go.Scatter(x=y, y=x, mode="lines", name=reg["title"])

                fig.add_trace(trace, row=1, col=idx)
                fig.update_xaxes(title_text=reg["y_col"], row=1, col=idx)
                fig.update_yaxes(title_text=reg["x_col"], row=1, col=idx)
            elif reg["kind"] == "notes":
                if reg.get("annotations"):
                    existing = list(fig.layout.annotations) if fig.layout.annotations else []
                    fig.update_layout(annotations=existing + reg["annotations"])
            elif reg["kind"] == "timeline":
                for t in reg["traces"]:
                    fig.add_trace(t, row=1, col=idx)

                fig.update_xaxes(title_text="Task", row=1, col=idx)
                fig.update_yaxes(title_text="Time (s)", row=1, col=idx)

                if reg.get("annotations"):
                    existing = list(fig.layout.annotations) if fig.layout.annotations else []
                    fig.update_layout(annotations=existing + reg["annotations"])

        fig.update_layout(
            title=self.title,
            width=420 * n_cols,
            height=600,
            margin=dict(t=80, l=60),
            dragmode="zoom",
            barmode="overlay"
        )

        return fig

