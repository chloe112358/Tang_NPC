import pytest

import tang_dialogue_test as dialogue


def test_get_api_key_for_scene_uses_scene_specific_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY_THEATER", "theater-key")
    monkeypatch.setenv("GEMINI_API_KEY", "legacy-key")

    assert dialogue._get_api_key_for_scene(1) == "theater-key"


def test_get_api_key_for_scene_falls_back_to_legacy_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY_FOOD", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "legacy-key")

    assert dialogue._get_api_key_for_scene(2) == "legacy-key"


def test_get_api_key_for_scene_requires_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY_TBD", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        dialogue._get_api_key_for_scene(3)

    assert "GEMINI_API_KEY_TBD" in str(exc_info.value)


def test_clean_npc_reply_text_removes_prompt_markdown():
    text = "哎呀，郎君可是覺得熱了？**不過啊**，您瞧我們這馬車。"

    cleaned = dialogue._clean_npc_reply_text(text)

    assert "**" not in cleaned
    assert "不過啊" in cleaned
    assert "您瞧我們這馬車" in cleaned


def test_clean_npc_reply_text_varies_repeated_transition():
    text = "不過啊，這木料有學問。不過啊，榫卯不用鐵釘也能穩固。"

    cleaned = dialogue._clean_npc_reply_text(text)

    assert cleaned.count("不過啊") == 1
    assert "這木料有學問" in cleaned
    assert "榫卯不用鐵釘" in cleaned


def test_clean_npc_reply_text_removes_formulaic_but_prefix():
    text = "哎呀，這個在下可不敢妄言。不過說起車輿工藝，那可是東市拿手絕活。"

    cleaned = dialogue._clean_npc_reply_text(text)

    assert "不過說起" not in cleaned
    assert "說起車輿工藝" in cleaned
