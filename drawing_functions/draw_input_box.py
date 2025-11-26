import pygame
from config import font, small_font
from colors import COLORS
import math
for name, value in COLORS.items():
    globals()[name] = value

GLOBAL_CLIPBOARD = ""

MONTHS = ["January", "February","March","April","May","June","July","August","September","October","November","December"]
MONTH_ABBR = {m[:3].lower(): m for m in MONTHS}

def adjust_color(color, amount):
    r, g, b = color
    return (
        max(0, min(255, r + amount)),
        max(0, min(255, g + amount)),
        max(0, min(255, b + amount)),
    )

# ============================================================
# UNIVERSAL INPUT BOX STATE CLASS (per-instance)
# ============================================================

class InputBox:
    def __init__(self, rect, text="", multiline=False, fontsize=0.06, box_type="text"):
        self.rect = rect
        self.text = text
        self.multiline = multiline
        self.fontsize = fontsize
        self.box_type = box_type  # "text", "month", "day", etc.

        # focus
        self.active = False

        # caret
        self.caret = 0              # for single-line
        self.caret_line = 0         # for multi-line
        self.caret_col = 0          # for multi-line

        # selection
        self.sel_start = 0
        self.sel_end = 0
        self.selecting = False      # dragging selection with mouse?

        # drag tracking
        self.drag_start_index = None

        # clipboard (you can also use pygame.scrap if desired)
        self.clipboard = ""

        # used when clicking, before you know if it's multi-line
        self._cached_lines = []

        # month / autofill helpers
        self.saved_text = text      # original value to revert to
        self.autofill_text = ""     # gray tail for month suggestions
        self.pending_full_month = None  # full month name if we have a valid partial

        # prevents auto-fill from overwriting user typing every frame
        self.initialized = False

# ============================================================
# CARET POSITION HELPERS
# ============================================================

def caret_from_click_single(render_font, text, click_x, box_x):
    rel_x = click_x - (box_x + 5)
    if rel_x <= 0:
        return 0

    for i in range(len(text) + 1):
        if render_font.size(text[:i])[0] >= rel_x:
            return i
    return len(text)

def wrap_text(render_font, text, max_width):
    """Returns wrapped lines. Breaks long words if needed."""
    text = "" if text is None else str(text)

    words = text.split(" ")
    lines = []
    cur = ""

    for w in words:
        test = cur + (" " if cur else "") + w

        # If whole word fits normally
        if render_font.size(test)[0] <= max_width:
            cur = test
            continue

        # If the word itself is too long → force-break it
        if render_font.size(w)[0] > max_width:
            # Flush current buffer
            if cur:
                lines.append(cur)
                cur = ""

            # Force-break the long word into pieces
            piece = ""
            for ch in w:
                if render_font.size(piece + ch)[0] <= max_width:
                    piece += ch
                else:
                    lines.append(piece)
                    piece = ch
            if piece:
                cur = piece  # remaining part of word stays in current line
            continue

        # Normal wrap
        if cur:
            lines.append(cur)
        cur = w

    if cur:
        lines.append(cur)

    if not lines:
        lines = [""]

    return lines


def caret_from_click_multi(render_font, lines, rect, click_pos):
    mx, my = click_pos
    line_h = render_font.get_height() - 4

    rel_y = my - rect.y
    line_idx = rel_y // line_h
    line_idx = max(0, min(line_idx, len(lines) - 1))
    text_line = lines[line_idx]

    rel_x = mx - (rect.x + 5)
    if rel_x <= 0:
        return (line_idx, 0)

    for i in range(len(text_line) + 1):
        if render_font.size(text_line[:i])[0] >= rel_x:
            return (line_idx, i)

    return (line_idx, len(text_line))


def global_index_from_line_col(lines, line_idx, col):
    """Convert (line, col) to absolute index in full text."""
    index = 0
    for i in range(line_idx):
        index += len(lines[i]) + 1  # +1 for space/newline (our wrapper uses spaces)
    return index + col

def _update_month_autofill(box: InputBox):
    """Update autofill_text and pending_full_month based on current typed prefix."""
    prefix = (box.text or "").strip()
    if not prefix:
        box.autofill_text = ""
        box.pending_full_month = None
        return

    low = prefix.lower()
    for m in MONTHS:
        ml = m.lower()
        if ml.startswith(low):
            box.pending_full_month = m
            box.autofill_text = m[len(prefix):]
            return

    box.pending_full_month = None
    box.autofill_text = ""


def _finalize_month_input(box: InputBox):
    """On blur / Tab: commit full month if valid partial; otherwise revert to saved_text."""
    prefix = (box.text or "").strip()

    # If we already have a pending full month from autofill, just commit it.
    if box.pending_full_month:
        box.text = box.pending_full_month
    else:
        # Try to match full/abbr manually
        low = prefix.lower()
        committed = False
        if low:
            for m in MONTHS:
                ml = m.lower()
                if low == ml or low == ml[:3]:
                    box.text = m
                    committed = True
                    break

        if not committed:
            # Revert to whatever we had saved when focus was gained
            box.text = box.saved_text

    box.autofill_text = ""
    box.pending_full_month = None
    box.caret = len(box.text)
    box.sel_start = box.caret
    box.sel_end = box.caret

# ============================================================
# LOGIC HANDLER (typing, arrows, selection, ctrl+a/c/v/x)
# ============================================================

def logic_input_box(event, box: InputBox, screen):
    """
    Handles clicking, dragging, arrow keys, typing, ctrl+A/C/V/X,
    selection & caret movement.
    Returns updated InputBox.
    """
    global GLOBAL_CLIPBOARD

    # --- detect activation change (works for Tab) ---
    if box.active and not getattr(box, "_prev_active", False):

        # month boxes should clear on focus
        if box.box_type == "month":
            box.saved_text = box.text
            box.text = ""
            box.autofill_text = ""
            box.pending_full_month = None
            box.caret = 0
            box.sel_start = 0
            box.sel_end = 0

        else:
            # non-month boxes: reset caret to end
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret

    # remember active state for next frame
    box._prev_active = box.active

    # build font for measurement
    sh = screen.get_height()
    render_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * box.fontsize))

    # wrap if multiline -> store cached lines
    if box.multiline:
        box._cached_lines = wrap_text(render_font, box.text, box.rect.width - 10)

    # ---------------------------------------------------------
    # PASSWORD FIELD — DISABLE: selection, ctrl shortcuts,
    # mouse-drag, highlight, copy, paste, cut.
    # ---------------------------------------------------------
    if box.box_type == "password":
        # Mouse clicks only move caret—never select
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if box.rect.collidepoint(event.pos):
                box.active = True
                box.selecting = False
                # move caret based on click x
                caret = caret_from_click_single(render_font, box.text, event.pos[0], box.rect.x)
                box.caret = caret
            else:
                box.active = False
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # NO dragging selection
        if event.type == pygame.MOUSEMOTION and box.active:
            return box
        if event.type == pygame.MOUSEBUTTONUP:
            return box

        # Ignore Ctrl+A, Ctrl+C, Ctrl+X, Ctrl+V
        if event.type == pygame.KEYDOWN:
            mod = pygame.key.get_mods()
            if mod & pygame.KMOD_CTRL:
                return box

    # ---------------------------------------------------------
    # FOCUS / CLICK TO SET CARET
    # ---------------------------------------------------------
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # If this click is on any spinner arrow, we DO NOT activate the input box
        if hasattr(box, "blocked_regions") and any(r.collidepoint(event.pos) for r in box.blocked_regions):
            return box

        if box.rect.collidepoint(event.pos):
            was_active = box.active
            box.active = True
            box.selecting = True


            # Month: on first focus, save existing text and clear for input
            if box.box_type == "month" and not was_active:
                box.saved_text = box.text
                box.text = ""
                box.autofill_text = ""
                box.pending_full_month = None
                box.caret = 0
                box.sel_start = 0
                box.sel_end = 0

            # TIME: clear on first focus (no autofill, just raw 4-digit time typing)
            if box.box_type == "time" and not was_active:
                box.saved_text = box.text
                box.text = ""
                box.caret = 0
                box.sel_start = 0
                box.sel_end = 0

            # compute caret position
            if not box.multiline:

                # FORCE caret to right side for number boxes (ignores click position)
                if box.box_type == "number":
                    box.caret = len(box.text)
                    box.sel_start = box.caret
                    box.sel_end = box.caret

                else:
                    caret = caret_from_click_single(render_font, box.text, event.pos[0], box.rect.x)
                    box.caret = caret
                    box.sel_start = caret
                    box.sel_end = caret

            else:
                lines = box._cached_lines if box._cached_lines else [""]
                (ln, col) = caret_from_click_multi(render_font, lines, box.rect, event.pos)
                box.caret_line = ln
                box.caret_col = col
                abs_idx = global_index_from_line_col(lines, ln, col)
                box.sel_start = abs_idx
                box.sel_end = abs_idx

            box.drag_start_index = box.sel_start

        else:
            # clicked outside → lose focus
            if box.active:
                if box.box_type == "month":
                    _finalize_month_input(box)

                # NUMBER: blank becomes "0" on blur
                elif box.box_type == "number":
                    if box.text.strip() == "":
                        box.text = "0"

                # SPOONS behave like number but you already cap them elsewhere
                elif box.box_type == "spoons":
                    if box.text.strip() == "":
                        box.text = "0"
                
                # TIME: If empty on blur, revert to last saved (or keep blank)
                elif box.box_type == "time":
                    if box.text.strip() == "":
                        box.text = box.saved_text


            box.active = False
            box.selecting = False

        return box

    # ---------------------------------------------------------
    # DRAG SELECTION
    # ---------------------------------------------------------
    if event.type == pygame.MOUSEMOTION and box.active and box.selecting:
        if box.rect.collidepoint(event.pos):

            if not box.multiline:
                if box.box_type == "number" or box.box_type == "spoons":
                    # number fields do not allow selection; caret always at end
                    box.caret = len(box.text)
                    box.sel_start = box.caret
                    box.sel_end = box.caret

                else:
                    caret = caret_from_click_single(render_font, box.text, event.pos[0], box.rect.x)
                    box.caret = caret

                    # Proper single-line drag selection:
                    if box.drag_start_index is None:
                        box.drag_start_index = caret

                    box.sel_start = box.drag_start_index
                    box.sel_end = caret


            else:
                lines = box._cached_lines if box._cached_lines else [""]
                (ln, col) = caret_from_click_multi(render_font, lines, box.rect, event.pos)
                box.caret_line = ln
                box.caret_col = col
                abs_idx = global_index_from_line_col(lines, ln, col)
                box.sel_end = abs_idx

        return box

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        box.selecting = False
        return box

    # ---------------------------------------------------------
    # KEYBOARD INPUT (only if active)
    # ---------------------------------------------------------
    if not box.active or event.type != pygame.KEYDOWN:
        return box

    mod = pygame.key.get_mods()
    ctrl = mod & pygame.KMOD_CTRL

    # GLOBAL TAB HANDLING (never type a tab!)
    if event.key == pygame.K_TAB:
        # If entering the month box via tab, clear it like a click would
        if box.box_type == "month":
            box.saved_text = box.text
            box.text = ""
            box.autofill_text = ""
            box.pending_full_month = None
            box.caret = 0
            box.sel_start = 0
            box.sel_end = 0
        return box


    # selection helpers
    def get_selection():
        lo = min(box.sel_start, box.sel_end)
        hi = max(box.sel_start, box.sel_end)
        return lo, hi

    def delete_selection():
        lo, hi = get_selection()
        box.text = box.text[:lo] + box.text[hi:]
        box.caret = lo
        box.sel_start = lo
        box.sel_end = lo

    # ---------------------------------------------------------
    # CTRL+A (select all)
    # ---------------------------------------------------------
    if ctrl and event.key == pygame.K_a:
        box.sel_start = 0
        box.sel_end = len(box.text)
        return box

    # ---------------------------------------------------------
    # CTRL+C
    # ---------------------------------------------------------
    if ctrl and event.key == pygame.K_c:
        lo, hi = get_selection()
        GLOBAL_CLIPBOARD = box.text[lo:hi]
        box.clipboard = GLOBAL_CLIPBOARD
        return box

    # ---------------------------------------------------------
    # CTRL+X (cut)
    # ---------------------------------------------------------
    if ctrl and event.key == pygame.K_x:
        lo, hi = get_selection()
        GLOBAL_CLIPBOARD = box.text[lo:hi]
        box.clipboard = GLOBAL_CLIPBOARD
        delete_selection()
        return box


    # ---------------------------------------------------------
    # CTRL+V (paste) with limits
    # ---------------------------------------------------------
    if ctrl and event.key == pygame.K_v:
        delete_selection()
        ins = GLOBAL_CLIPBOARD or ""
        if ins == "":
            return box

        # ----- SPOONS NUMBER (cap at 10) -----
        if box.box_type == "spoons":
            temp = box.text[:box.caret] + ins + box.text[box.caret:]
            digits = "".join(ch for ch in temp if ch.isdigit())
            digits = digits.lstrip("0")
            if digits == "":
                val = 0
            else:
                try:
                    val = int(digits)
                except:
                    return box
            if val > 10:
                val = 10
            box.text = "" if val == 0 else str(val)
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # ----- NUMBER (unlimited, no cap) -----
        if box.box_type == "number":
            temp = box.text[:box.caret] + ins + box.text[box.caret:]
            # keep digits only; allow empty
            digits = "".join(ch for ch in temp if ch.isdigit())
            box.text = digits
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # ----- MONTH input: treat paste as prefix & update autofill -----
        if box.box_type == "month":
            prefix = box.text[:box.caret] + ins + box.text[box.caret:]
            box.text = prefix.strip()
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            _update_month_autofill(box)
            return box

        # ----- DAY: enforce 1–31, max 2 digits -----
        if box.box_type == "day":
            temp = box.text[:box.caret] + ins + box.text[box.caret:]
            digits = "".join(ch for ch in temp if ch.isdigit())
            digits = digits[:2]
            if digits == "":
                return box
            try:
                val = int(digits)
            except:
                return box
            if not (1 <= val <= 31):
                return box
            box.text = str(val)
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # ----- TIME: store up to 4 digits, formatting done in draw -----
        if box.box_type == "time":
            temp = box.text[:box.caret] + ins + box.text[box.caret:]
            digits = "".join(ch for ch in temp if ch.isdigit())
            digits = digits[:4]
            box.text = digits
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # ----- DEFAULT TEXT (task name, description, positive_int, etc.) -----
        new_text = box.text[:box.caret] + ins + box.text[box.caret:]

        # Multiline: enforce 3 lines max, using same wrapping and padding
        if box.multiline:
            usable_width = box.rect.width - 12
            lines = wrap_text(render_font, new_text, usable_width)
            if len(lines) > 3:
                return box  # reject paste that would overflow to 4th line

        # Single-line text: enforce width cap to avoid overflow
        if box.box_type == "text" and not box.multiline:
            if render_font.size(new_text)[0] > (box.rect.width - 12):
                return box  # reject paste that would overflow box width

        # Accept new text
        box.text = new_text
        box.caret += len(ins)
        box.sel_start = box.caret
        box.sel_end = box.caret

        # Keep caret_line / caret_col in sync for multiline
        if box.multiline:
            usable_width = box.rect.width - 12
            lines = wrap_text(render_font, box.text, usable_width)
            abs_i = box.caret
            running = 0
            for li, ln in enumerate(lines):
                if abs_i <= running + len(ln):
                    box.caret_line = li
                    box.caret_col = abs_i - running
                    break
                running += len(ln) + 1

        return box


    # ---------------------------------------------------------
    # Backspace
    # ---------------------------------------------------------
    if event.key == pygame.K_BACKSPACE:
        lo, hi = get_selection()
        if lo != hi:
            delete_selection()
        elif box.caret > 0:
            box.text = box.text[:box.caret - 1] + box.text[box.caret:]
            box.caret -= 1
        box.sel_start = box.caret
        box.sel_end = box.caret

        if box.box_type == "month":
            _update_month_autofill(box)

        return box

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------
    if event.key == pygame.K_DELETE:
        lo, hi = get_selection()
        if lo != hi:
            delete_selection()
        elif box.caret < len(box.text):
            box.text = box.text[:box.caret] + box.text[box.caret + 1:]
        if box.box_type == "month":
            _update_month_autofill(box)
        return box

    # ---------------------------------------------------------
    # Arrow Keys
    # ---------------------------------------------------------
    if event.key == pygame.K_LEFT:
        if box.caret > 0:
            box.caret -= 1
        box.sel_start = box.caret
        box.sel_end = box.caret
        return box

    if event.key == pygame.K_RIGHT:
        if box.caret < len(box.text):
            box.caret += 1
        box.sel_start = box.caret
        box.sel_end = box.caret
        return box

    # ---------------------------------------------------------
    # CHARACTER TYPING
    # ---------------------------------------------------------

    # filter inputs the stardew valley font cannot render
    disallowed = {"[", "]", "|", "\\", "<", "\n", "\r", "`"}

    # event.unicode gives the literal character typed
    ch = event.unicode

    # ignore anything typed while holding Ctrl (ctrl+a, ctrl+s, ctrl+p, etc.)
    mod = pygame.key.get_mods()
    ctrl = mod & pygame.KMOD_CTRL
    if ctrl:
        return box

    # ignore forbidden characters
    if ch in disallowed:
        return box

    # ignore enter/return by key code as well
    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        return box

    # if unicode is empty or None, ignore it
    if not ch:
        return box


    if ch:
        # -----------------------------------------
        # Only digits allowed for number/day/time
        # -----------------------------------------
        if box.box_type in ("number", "day", "time"):
            if not ch.isdigit():
                return box  # ignore non-digits

        # -----------------------------------------
        # SPOONS NUMBER (cap at 10)
        # -----------------------------------------
        if box.box_type == "spoons":
            delete_selection()
            new_text = box.text[:box.caret] + ch + box.text[box.caret:]
            new_text = new_text.lstrip("0")
            if new_text == "":
                val = 0
            else:
                try:
                    val = int(new_text)
                except:
                    return box
            if val > 10:
                val = 10
            box.text = "" if val == 0 else str(val)
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # -----------------------------------------
        # NUMBER (unlimited, no cap)
        # -----------------------------------------
        if box.box_type == "number":
            delete_selection()
            # insert digit normally
            new_text = box.text[:box.caret] + ch + box.text[box.caret:]
            # keep only digits, but allow empty string
            new_text = "".join(c for c in new_text if c.isdigit())
            box.text = new_text
            # caret always at end for cleanliness
            box.caret = len(box.text)
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # -----------------------------------------
        # Month input: keep prefix, gray autofill tail
        # -----------------------------------------
        if box.box_type == "month":
            delete_selection()
            prefix = box.text[:box.caret] + ch + box.text[box.caret:]
            box.text = prefix
            box.caret = len(prefix)
            box.sel_start = box.caret
            box.sel_end = box.caret
            _update_month_autofill(box)
            return box

        # -----------------------------------------
        # DAY: enforce range 1–31
        # -----------------------------------------
        if box.box_type == "day":
            delete_selection()
            new_text = box.text[:box.caret] + ch + box.text[box.caret:]

            # Force max 2 digits
            if len(new_text) > 2:
                return box

            # Validate numeric value
            try:
                val = int(new_text)
                if not (1 <= val <= 31):
                    return box
            except:
                return box

            box.text = new_text
            box.caret += 1
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # -----------------------------------------
        # TIME: store raw digits, formatting done in draw
        # -----------------------------------------
        if box.box_type == "time":
            delete_selection()
            new_text = box.text[:box.caret] + ch + box.text[box.caret:]

            # Limit to 4 digits max
            if len(new_text) > 4:
                return box

            box.text = new_text
            box.caret += 1
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # -----------------------------------------
        # PASSWORD MODE (single-line, fully masked)
        # -----------------------------------------
        if box.box_type == "password":
            # No selection, no delete_selection()
            if ch.isprintable():
                box.text = box.text[:box.caret] + ch + box.text[box.caret:]
                box.caret += 1
            box.sel_start = box.caret
            box.sel_end = box.caret
            return box

        # -----------------------------------------
        # DEFAULT TEXT MODE
        # -----------------------------------------
        delete_selection()
        new_text = box.text[:box.caret] + ch + box.text[box.caret:]

        # enforce multiline limit of 3 lines
        if box.multiline:
            usable_width = box.rect.width - 12
            lines = wrap_text(render_font, new_text, usable_width)

            if len(lines) > 3:
                return box  # reject new character
            
        if box.box_type == "text" and not box.multiline:
            # width cap = rect.width - 12px padding
            if render_font.size(new_text)[0] > (box.rect.width - 12):
                return box  # reject character

        # accept new text
        box.text = new_text
        box.caret += len(ch)
        box.sel_start = box.caret
        box.sel_end = box.caret

        # --- NEW: update caret_line and caret_col for multiline boxes ---
        if box.multiline:
            usable_width = box.rect.width - 12
            lines = wrap_text(render_font, box.text, usable_width)
            abs_i = box.caret
            running = 0
            for li, ln in enumerate(lines):
                if abs_i <= running + len(ln):
                    box.caret_line = li
                    box.caret_col = abs_i - running
                    break
                running += len(ln) + 1

        return box

# ============================================================
# MATH HELPERS (text width → x coordinate)
# ============================================================

def _text_width(render_font, text):
    return render_font.size(text)[0]

def _draw_selection_single(screen, rect, render_font, text, text_x, text_y, sel_start, sel_end):
    """Draw highlight behind selected characters for single-line."""
    if sel_start == sel_end:
        return

    lo = min(sel_start, sel_end)
    hi = max(sel_start, sel_end)

    prefix = text[:lo]
    middle = text[lo:hi]

    px = text_x + _text_width(render_font, prefix)
    pw = _text_width(render_font, middle)
    py = text_y
    ph = render_font.get_height()

    pygame.draw.rect(screen, (100,140,255), (px, py, pw, ph))



def _draw_selection_multi(screen, rect, render_font, lines, line_h, caret_positions, sel_start, sel_end):
    """Draw selection highlight for multi-line mode."""
    if sel_start == sel_end:
        return

    lo = min(sel_start, sel_end)
    hi = max(sel_start, sel_end)

    current_index = 0   # global index through full text

    for i, line in enumerate(lines):
        line_len = len(line)

        line_start = current_index
        line_end   = current_index + line_len

        # does this line have any selected part?
        if line_end < lo or line_start > hi:
            # no overlap
            current_index += line_len + 1
            continue

        # segment real selection range
        seg_start = max(0, lo - line_start)
        seg_end   = min(line_len, hi - line_start)

        prefix = line[:seg_start]
        middle = line[seg_start:seg_end]

        px = rect.x + 5 + _text_width(render_font, prefix)
        pw = _text_width(render_font, middle)
        py = rect.y + 5 + i * line_h
        ph = line_h

        pygame.draw.rect(screen, (100,140,255), (px, py, pw, ph))  # highlight

        current_index += line_len + 1


# ============================================================
# MASTER INPUT BOX WITH SELECTION SUPPORT
# ============================================================

# ============================================================
# MASTER INPUT BOX WITH SELECTION + TYPE SUPPORT
# ============================================================

def draw_input_box(
        screen,
        obj,                    # can be InputBox OR just a rect
        active_color,
        inactive_color,
        text=None,
        active=None,
        centered=False,
        background_color=None,
        infill=None,
        pullUp=0,
        fontsize=0.06,
        caret_pos=None,
        caret_line=None,
        caret_col=None,
        selection_start=None,
        selection_end=None,
        multiline=None,
        blink_interval=500
    ):
    """
    Universal drawer:
    - If obj is InputBox => pull all fields from it
    - If obj is rect => use legacy params (rect, text, active)
    """
        
    # ------------------------------------------------------------
    # Determine whether using InputBox mode or legacy mode
    # ------------------------------------------------------------
    if isinstance(obj, InputBox):
        box = obj
        box_type = box.box_type   # define FIRST

        # password boxes are ALWAYS single-line and have no selection
        if box_type == "password":
            multiline = False
            box.multiline = False
            box.sel_start = 0
            box.sel_end = 0
            box.selecting = False

        rect = box.rect
        active = box.active
        text = box.text
        multiline = box.multiline
        fontsize = box.fontsize

        caret_pos = box.caret
        caret_line = box.caret_line
        caret_col = box.caret_col
        selection_start = box.sel_start
        selection_end = box.sel_end

        text = "" if text is None else str(text)

    else:
        # legacy mode (obj is rect)
        rect = obj
        box_type = "text"   # no special behavior
        if multiline is None:
            multiline = False

    # ------------------------------------------------------------
    # Start drawing
    # ------------------------------------------------------------
    sw, sh = screen.get_size()
    render_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * fontsize))

    # Fade-out flash timer
    if isinstance(obj, InputBox) and hasattr(obj, "flash_timer") and obj.flash_timer > 0:
        now = pygame.time.get_ticks()
        dt = now - getattr(obj, "_last_flash_tick", now)
        obj.flash_timer = max(0, obj.flash_timer - dt)
        obj._last_flash_tick = now
        if obj.flash_timer <= 0:
            obj.flash_error = False

    border_col = active_color if active else inactive_color

    # ---- Infill background ----
    if infill and background_color is not None:
        if infill == "light":   fill_col = adjust_color(background_color, 20)
        elif infill == "lighter": fill_col = adjust_color(background_color, 40)
        elif infill == "dark":  fill_col = adjust_color(background_color, -20)
        elif infill == "darker": fill_col = adjust_color(background_color, -40)
        else: fill_col = background_color
        pygame.draw.rect(screen, fill_col, rect)

    old_clip = screen.get_clip()
    screen.set_clip(rect)

    # ============================================================
    # SINGLE-LINE
    # ============================================================
    if not multiline:
        base_text = "" if text is None else str(text)

        # -------- PASSWORD MASKING --------
        if box_type == "password":
            disp_text = "=" * len(base_text)   # bullet character
        else:
            disp_text = base_text


        # ------- TIME formatting -------
        if box_type == "time":
            if len(base_text) == 3:
                disp_text = base_text[0] + ":" + base_text[1:]
            elif len(base_text) == 4:
                disp_text = base_text[:2] + ":" + base_text[2:]
            else:
                disp_text = base_text

        # Month autofill: base + gray tail
        month_tail = ""
        if isinstance(obj, InputBox) and box_type == "month":
            month_tail = box.autofill_text or ""
            disp_text = base_text + month_tail

        txt_surface = render_font.render(disp_text, True, BLACK) #type: ignore

        if centered:
            text_x = rect.x + (rect.width - txt_surface.get_width()) // 2
        else:
            text_x = rect.x + 5

        text_y = rect.y + (rect.height - txt_surface.get_height()) // 2 - pullUp

        # Selection highlight (based only on the editable base_text)
        if box_type != "password" and active:
            if selection_start is not None and selection_end is not None:
                _draw_selection_single(screen, rect, render_font, base_text, text_x, text_y, selection_start, selection_end)

        # Draw text:
        # - if month with tail: draw base in black, tail in gray
        # - else: just draw disp_text
        if box_type == "month" and month_tail:
            base_surface = render_font.render(base_text, True, BLACK) #type: ignore
            screen.blit(base_surface, (text_x, text_y))
            tail_x = text_x + base_surface.get_width()
            tail_surface = render_font.render(month_tail, True, (160, 160, 160))
            screen.blit(tail_surface, (tail_x, text_y))
            txt_height = base_surface.get_height()
        else:
            screen.blit(txt_surface, (text_x, text_y))
            txt_height = txt_surface.get_height()

        # Caret (positioned within base_text only)
        if active and caret_pos is not None and (pygame.time.get_ticks() // blink_interval) % 2 == 0:
            prefix = base_text[:caret_pos]
            # ---- CARET POSITION ----
            if active and caret_pos is not None and (pygame.time.get_ticks() // blink_interval) % 2 == 0:

                # determine display string (this matches exactly what you drew above)
                if box_type == "time":
                    raw = base_text.replace(":", "")
                    if len(raw) == 3:
                        disp_for_caret = raw[0] + ":" + raw[1:]
                    elif len(raw) == 4:
                        disp_for_caret = raw[:2] + ":" + raw[2:]
                    else:
                        disp_for_caret = raw
                else:
                    disp_for_caret = base_text

                # compute caret x correctly
                caret_x = rect.x + 5 + render_font.size(disp_for_caret[:caret_pos])[0]

                pygame.draw.line(screen, BLACK, (caret_x, text_y), (caret_x, text_y + txt_height), 2) #type: ignore

    # ============================================================
    # MULTI-LINE
    # ============================================================
    else:
        text = "" if text is None else str(text)
        usable_width = box.rect.width - 12
        lines = wrap_text(render_font, text, usable_width)


        # Safety fix
        if not lines:
            lines = [""]
        if caret_line is None or caret_line >= len(lines):
            caret_line = len(lines) - 1
        if caret_col is None or caret_col > len(lines[caret_line]):
            caret_col = len(lines[caret_line])

        line_h = render_font.get_height() - 4

        # Highlight
        if active and selection_start is not None and selection_end is not None:
            _draw_selection_multi(screen, rect, render_font, lines, line_h, None, selection_start, selection_end)

        y = rect.y + 5 - pullUp
        for line in lines:
            screen.blit(render_font.render(line, True, BLACK), (rect.x + 5, y)) #type: ignore
            y += line_h

        # caret
        if active and caret_line is not None and caret_col is not None:
            if (pygame.time.get_ticks() // blink_interval) % 2 == 0:
                line_text = lines[caret_line]
                prefix = line_text[:caret_col]
                cx = rect.x + 5 + _text_width(render_font, prefix)
                cy1 = rect.y + 5 + caret_line * line_h
                pygame.draw.line(screen, BLACK, (cx, cy1), (cx, cy1 + line_h), 2) #type: ignore

    screen.set_clip(old_clip)

    # -------------------------
    # FLASH RED BORDER (only if box has flash fields)
    # -------------------------
    if isinstance(obj, InputBox) and hasattr(obj, "flash_error") and obj.flash_error and obj.flash_timer > 0:
        t = pygame.time.get_ticks()
        pulse = (math.sin(t * 0.03) + 1) / 2  # nice fade
        red = (255, 60, 60)
        mixed = (
            int(border_col[0] * (1 - pulse) + red[0] * pulse),
            int(border_col[1] * (1 - pulse) + red[1] * pulse),
            int(border_col[2] * (1 - pulse) + red[2] * pulse),
        )
        pygame.draw.rect(screen, mixed, rect, 4)
    else:
        pygame.draw.rect(screen, border_col, rect, 4)

