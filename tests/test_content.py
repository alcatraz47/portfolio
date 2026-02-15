from pathlib import Path

from app.content import clear_content_cache, load_content


def test_content_yaml_loads_expected_keys() -> None:
    clear_content_cache()
    data = load_content(Path("content/content.yaml"))

    assert data["site"]["name"] == "Zakia Sultana"
    assert data["site"]["location"] == "Germany & Norway"
    assert data["site"]["show_phone"] is False
    assert len(data["selected_work"]) == 4
    assert len(data["about"]["my_focus"]) == 3
    assert len(data["about"]["how_i_work"]) == 4
