from email.policy import default
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


def card_component(score, context, link, key=None):
    """Create a new instance of "card_component".
    """
    # the below initializes the react component (in CardComponent.tsx)
    _ = _component_func(
        score=score,
        context=context,
        link=link,
        key=key,
        default=0
    )


if not _RELEASE:
    import streamlit as st

    st.subheader("Component test")
    st.markdown("---")

    _ = card_component(
        score=0.88,
        context="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor...",
        link="https://google.com"
    )

    _ = card_component(
        score=1.65,
        context="B - Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor...",
        link="https://yahoo.com"
    )
