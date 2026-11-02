# Chinese Poem Text Art · 诗词以字成画

An Agent Skill for images in which the characters of a Chinese poem form its scene. It emphasizes one clear visual subject, a readable path through the whole poem, and exact Hanzi rendered with a real font when accuracy matters.

The concept is based on [李继刚分享的诗词文字画 Prompt](https://m.okjike.com/users/752D3103-1107-43A0-BA49-20EC29D09E36). This repository packages an expanded art-direction workflow and an optional deterministic PNG renderer.

## Install

Clone this repository into a skills directory, for example:

```bash
git clone https://github.com/LuckyE1120/chinese-poem-text-art.git ~/.agents/skills/chinese-poem-text-art
```

Then ask your agent: `使用 $chinese-poem-text-art，把《江雪》做成以字成画的图片。`

## Optional exact-text renderer

The renderer requires Python 3.10+ and Pillow. It uses a locally installed Chinese font; pass the path with `--font`.

```bash
python3 -m pip install Pillow
python3 scripts/render_text_art.py examples/jiangxue.json --font /path/to/Chinese-font.ttf --output jiangxue.png
```

The JSON describes the poem, colors, and character placements. The renderer checks that every scene character comes from the poem and draws the full poem in a reading area. Image models may be used for visual drafts, but their Chinese text needs direct inspection.

## Files

- `SKILL.md`: agent workflow and quality checks
- `references/art-direction.md`: reusable prompt and composition guidance
- `scripts/render_text_art.py`: exact-text PNG renderer
- `examples/jiangxue.json`: sample layout

## License

MIT. The linked original Prompt belongs to its author; this repository paraphrases and extends the method rather than republishing that text.
