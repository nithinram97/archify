# Screenshots for the ERM 2.0 trailer

The `react_*.png` files here are real screenshots of the ERM React app, rendered with invented sample
data by `../react-mock` (no Foundry, no real risks or people). Retake them from the live app if you prefer.
The Slate ones still need capturing by hand.

Drop real screenshots into this folder with the names below. The Blender script uses them instead of the
mock-ups automatically. Any missing file falls back to the mock-up of the same name.

**Before you capture**
- Use a dev or test dashboard with sample data only. No real risk titles, people's names or comments.
- Browser window about 1600 × 1000 (16:10), zoom 100%, no bookmarks bar, no personal tabs in view.
- Crop to the app area. PNG or JPG both work.

## Slate (the app users know today), shots 2 and 3

| File | What to show |
|---|---|
| `slate_heat.png` | Heat map tab with a few risks on it |
| `slate_table.png` | Report table tab |
| `slate_onepager.png` | One-pager tab |
| `slate_tracker.png` | Action tracker tab |

## React (ERM 2.0), the feature cards in shots 8 to 14

| File | What to show |
|---|---|
| `react_search.png` | Dashboard switcher open, a few letters typed, matching dashboards listed |
| `react_share.png` | The "link copied" message after copying a link to a tab |
| `react_slide.png` | Slideshow mode, a slide on screen |
| `react_filters.png` | Report table with the criticality-differs and category filters on, a column widened |
| `react_onepager_pick.png` | The fourth one-pager layout with custom slots, selection shortcuts visible |
| `react_report.png` | Report preview with the classification label and the cover page option |
| `react_locked.png` | A released (locked) dashboard with the permissions panel open |
| `react_toast.png` | The green "updated successfully" message after saving a risk |

Optional: `react_heat.png`, `react_table.png`, `react_onepager.png`, `react_tracker.png` are not used yet.

## Team logos (end card)

| File | What |
|---|---|
| `logo_skywise.png` | Official Skywise logo, transparent background, at least 600 px wide |
| `logo_clairvoyant.png` | Clairvoyant team logo, transparent background, at least 600 px wide |

Use the official files from brand or comms; don't redraw them. Until the files are in place, the end card shows the team names as text. If a logo is dark, set `LOGO_PLATE = '#f8fafc'` in `erm2_trailer.py` to put a light card behind it.
