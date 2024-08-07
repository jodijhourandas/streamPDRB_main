import json

from streamlit_elements import nivo, mui
from .dashboard import Dashboard


class Pie(Dashboard.Item):

    DEFAULT_DATA = [
        { "id": "java", "label": "java", "value": 465, "color": "hsl(128, 70%, 50%)" },
        { "id": "rust", "label": "rust", "value": 140, "color": "hsl(178, 70%, 50%)" },
        { "id": "scala", "label": "scala", "value": 40, "color": "hsl(322, 70%, 50%)" },
        { "id": "ruby", "label": "ruby", "value": 439, "color": "hsl(117, 70%, 50%)" },
        { "id": "elixir", "label": "elixir", "value": 366, "color": "hsl(286, 70%, 50%)" }
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._theme = {
            "dark": {
                "background": "#252526",
                "textColor": "#FAFAFA",
                "tooltip": {
                    "container": {
                        "background": "#3F3F3F",
                        "color": "FAFAFA",
                    }
                }
            },
            "light": {
                "background": "#FFFFFF",
                "textColor": "#31333F",
                "tooltip": {
                    "container": {
                        "background": "#FFFFFF",
                        "color": "#31333F",
                    }
                }
            }
        }

    def __call__(self, json_data):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            data = self.DEFAULT_DATA

        with mui.Paper(key=self._key, sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"}, elevation=7):
            with self.title_bar():
                mui.icon.PieChart()
                mui.Typography("Pie chart", sx={"flex": 1})

            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Pie(
                    data=data,
                    theme=self._theme["light" if self._dark_mode else "dark"],
                    margin={ "top": 30, "right": 70, "bottom": 70, "left": 70 },
                    innerRadius=0.5,
                    padAngle=0.7,
                    cornerRadius=3,
                    activeOuterRadiusOffset=8,
                    borderWidth=1,
                    borderColor={
                        "from": "color",
                        "modifiers": [
                            [
                                "darker",
                                0.2,
                            ]
                        ]
                    },
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsTextColor="grey",
                    arcLinkLabelsThickness=2,
                    arcLinkLabelsColor={ "from": "color" },
                    arcLabelsSkipAngle=10,
                    arcLabelsTextColor={
                        "from": "color",
                        "modifiers": [
                            [
                                "darker",
                                2
                            ]
                        ]
                    },
                    defs=[
                        {
                            "id": "dots",
                            "type": "patternDots",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "size": 4,
                            "padding": 1,
                            "stagger": True
                        },
                        {
                            "id": "lines",
                            "type": "patternLines",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "rotation": -45,
                            "lineWidth": 6,
                            "spacing": 10
                        }
                    ],
                    fill=[
                        { "match": { "id": "PKRT" }, "id": "dots" },
                        { "match": { "id": "LNPRT" }, "id": "dots" },
                        { "match": { "id": "KP" }, "id": "dots" },
                        { "match": { "id": "PMTB" }, "id": "dots" },
                        { "match": { "id": "Inventori" }, "id": "lines" },
                        { "match": { "id": "Ekspor" }, "id": "lines" },
                        { "match": { "id": "Impor" }, "id": "lines" },
                        { "match": { "id": "javascript" }, "id": "lines" }
                    ]
                )
