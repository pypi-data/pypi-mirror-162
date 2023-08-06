import os
import streamlit.components.v1 as components

_RELEASE = True


if not _RELEASE:
    _component_func = components.declare_component(
        "st_card_search_component",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_card_search_component", path=build_dir)


def card_search_component(name, key=None):
    component_value = _component_func(name=name, key=key, default=0)

    return component_value


def st_card_search_component(subtitle, body, link):
    """Create a new instance of "card_component".
    """
    # the below initializes the react component (in CardComponent.tsx)
    _ = _component_func(
        subtitle=subtitle,
        body=body,
        link=link
    )


if not _RELEASE:
    import streamlit as st

    st.subheader("Component test")
    st.markdown("---")

    _ = st_card_search_component(
        subtitle="A subtitle",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor...",
        link="https://google.com"
    )

    _ = st_card_search_component(
        subtitle="B subtitle",
        body="B - Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor...",
        link="https://yahoo.com"
    )
