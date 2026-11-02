---
name: chinese-poem-text-art
description: Create Chinese poetry images in which the poem's own readable Hanzi form the depicted scene. Use for 以字成画、诗词文字画 or requests to turn a Chinese poem into an image made from its characters; not for ordinary illustrated poetry posters.
---

# Chinese Poem Text Art · 诗词以字成画

Turn a Chinese poem into a picture whose visible objects are built from characters in that poem. The approved visual direction is a restrained typography artwork: one recognizable main image, two or three supporting motifs, strong scale contrast, and enough empty space to feel like a poem.

## Make the image

1. Establish the exact poem, author, and textual version. If the user supplies the text, use it. Otherwise check a reliable edition before composing; keep variants explicit when they matter.
2. List only things and spatial relationships present in the poem. Choose one strong main motif. Give it most of the visual weight; let the remaining motifs explain place, movement, or mood.
3. Map each motif to the word that names or describes it. A mountain should grow from `山`, a boat from `舟`, rain from `雨`, and so on. Repeat source characters when needed, but never use unrelated characters as filler. Place abstract, negative, or questioning words in the space between motifs instead of forcing them into objects.
4. Make the text itself carry the shape. Vary character size, spacing, direction, density, opacity, and reading distance. Favor a quiet palette and intentional negative space. Do not turn the result into a landscape illustration with text laid over it.
5. Preserve one clear path on which a reader can recover the entire poem in order. A separate but integrated reading area is acceptable when it improves accuracy.
6. Check the finished image at full size and thumbnail size. Reject missing or incorrect characters, extra characters, non-text scenery, unclear main motif, or an unreadable poem. Repair the failed part and recheck.

For a reusable art-direction prompt and composition patterns, read [references/art-direction.md](references/art-direction.md).

## Text accuracy

Image models can create compelling exploratory compositions, but their Chinese glyphs may be wrong. When exact poem text is important, render the final visible characters with a real Chinese font. `scripts/render_text_art.py` accepts a poem and a layout JSON file, checks that every visible scene character belongs to the poem, and writes a PNG. It does not invent the composition; design the layout for the poem first. See [examples/jiangxue.json](examples/jiangxue.json) for the format.

For image-model exploration, use the available image-generation tool. Treat any resulting image as a draft until the glyphs and reading path are checked. Use editing or deterministic typesetting to correct a draft; do not describe unchecked text as accurate.

## Deliver

Show the image, identify the poem and version used, and provide the saved file. If any glyphs or the reading path remain unverified, say so clearly. Attribute this workflow's original idea to [李继刚的诗词文字画 Prompt](https://m.okjike.com/users/752D3103-1107-43A0-BA49-20EC29D09E36) when sharing or publishing the method.
