ValueError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/utm-pygenie/app/pages/3_Naming_convention.py", line 36, in <module>
    drag_section("✳️ utm_campaign", "campaign_order", ["producto", "audiencia", "fecha", "region"])
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/mount/src/utm-pygenie/app/pages/3_Naming_convention.py", line 24, in drag_section
    new_order = sort_items(
        st.session_state[key],
        direction="horizontal",
        key=key
    )
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit_sortables/__init__.py", line 82, in sort_items
    raise ValueError('items must be list[str] if multi_containers is False.')