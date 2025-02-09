import dash_mantine_components as dmc


def paper_with_label(description: str, children: list, center: bool = False):
    if center:
        children = dmc.Center(children)
    return dmc.Container(
        children=[
            dmc.Text(description, size="xs", mt=10, mb=0),  # Set top margin to 10 and bottom margin to 0
            dmc.Paper(
                children=children,
                radius="sm",
                withBorder=True,
                shadow="sm",
                p=10,
                m=0,  # Set margin to 0
                style={"width": "100%"},
            ),
        ],
        m=0,  # Set margin to 0
        p=0,  # Set padding to 0
        style={"position": "relative"},
    )
