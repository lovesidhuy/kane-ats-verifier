"""In-DOM field scanner, value injector, and field-answer resolver."""

from __future__ import annotations

from typing import Any

from ats_verifier.form_answers import resolve_answer

SCAN_FIELDS_JS = r"""
(() => {
    let seq = 0;
    const fields = [];
    const clean = (txt) => (txt || '').replace(/\s+/g, ' ').replace(/[*:]+$/, '').trim();
    const visible = (el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden';
    };

    function labelFor(el) {
        const id = el.getAttribute('id');
        if (id) {
            try {
                const lbl = document.querySelector(`label[for="${CSS.escape(id)}"]`);
                if (lbl && visible(lbl)) return clean(lbl.innerText || lbl.textContent);
            } catch (_) {}
        }
        const wrap = el.closest('label');
        if (wrap) {
            const copy = wrap.cloneNode(true);
            copy.querySelectorAll('input, select, textarea, button').forEach((n) => n.remove());
            const txt = clean(copy.innerText || copy.textContent);
            if (txt) return txt;
        }
        return clean(
            el.getAttribute('aria-label') ||
            el.getAttribute('placeholder') ||
            el.getAttribute('name') ||
            el.getAttribute('id') ||
            ''
        );
    }

    for (const el of document.querySelectorAll('input, textarea, select')) {
        const tag = el.tagName.toLowerCase();
        const type = tag === 'select' ? 'select' : (el.getAttribute('type') || 'text').toLowerCase();
        if (['hidden', 'file', 'submit', 'button', 'reset', 'image', 'radio', 'checkbox'].includes(type)) {
            continue;
        }
        if (!visible(el)) continue;
        const label = labelFor(el);
        if (!label) continue;
        const fid = `ats_field_${++seq}`;
        el.setAttribute('data-ats-field-id', fid);
        const item = {
            id: el.getAttribute('id') || fid,
            ats_field_id: fid,
            tag,
            type,
            label,
            name: el.getAttribute('name') || '',
            current_value: el.value || '',
            _frame_index: 0,
        };
        if (tag === 'select') {
            item.options = Array.from(el.options).map((o) => clean(o.text || o.value)).filter(Boolean);
        }
        fields.push(item);
    }
    return fields;
})()
"""

INJECT_VALUES_JS = r"""
((payload) => {
    let filledCount = 0;
    for (const item of payload || []) {
        const id = item.id;
        const val = item.value;
        if (val === undefined || val === null || val === '') continue;
        const el =
            document.getElementById(id) ||
            document.querySelector(`[name="${CSS.escape(String(id))}"]`) ||
            document.querySelector(`[data-ats-field-id="${CSS.escape(String(id))}"]`);
        if (!el) continue;
        if (el.tagName.toLowerCase() === 'select') {
            const target = String(val).toLowerCase().trim();
            for (let i = 0; i < el.options.length; i++) {
                const opt = el.options[i];
                const txt = (opt.text || '').toLowerCase().trim();
                const ov = (opt.value || '').toLowerCase().trim();
                if (txt === target || ov === target || txt.includes(target)) {
                    el.selectedIndex = i;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    filledCount++;
                    break;
                }
            }
        } else {
            el.focus();
            el.value = String(val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
            filledCount++;
        }
    }
    return filledCount;
})
"""


class DOMAutofillEngine:
    """Resolve scanned DOM fields against a candidate profile and policy bank."""

    @classmethod
    def resolve_field_answers(
        cls,
        fields: list[dict[str, Any]],
        profile: dict[str, Any],
        job_context: str = "",
    ) -> list[dict[str, Any]]:
        first = str(profile.get("first_name", ""))
        last = str(profile.get("last_name", ""))
        full = str(profile.get("full_name") or f"{first} {last}".strip())

        known_map = {
            "first name": first,
            "last name": last,
            "full name": full,
            "name": full,
            "email": str(profile.get("email", "")),
            "email address": str(profile.get("email", "")),
            "phone": str(profile.get("phone", "")),
            "phone number": str(profile.get("phone", "")),
            "linkedin": str(profile.get("linkedin", "")),
            "linkedin url": str(profile.get("linkedin", "")),
            "linkedin profile": str(profile.get("linkedin", "")),
            "city": str(profile.get("city", "")),
            "location": str(profile.get("location", "")),
            "why are you interested in this role?": str(
                profile.get("cover_letter") or profile.get("why_company_answer") or ""
            ),
            "why are you interested in this role": str(
                profile.get("cover_letter") or profile.get("why_company_answer") or ""
            ),
        }

        payload: list[dict[str, Any]] = []
        for field in fields:
            label = str(field.get("label", "")).strip()
            if not label:
                continue
            curr = str(field.get("current_value", "")).strip()
            if curr and curr.lower() not in {"select...", "choose...", "select an option"}:
                continue

            clean_lbl = label.lower().replace("*", "").replace(":", "").strip()
            val = known_map.get(clean_lbl, "")
            if not val:
                resolved = resolve_answer(
                    question=label,
                    options=field.get("options"),
                    job_context=job_context,
                    profile=profile,
                    allow_ai=False,
                )
                val = resolved.value

            if val:
                key = field.get("id") or field.get("name")
                payload.append(
                    {
                        "id": key,
                        "type": field.get("type", "text"),
                        "value": val,
                        "radio_options": field.get("radio_options", []),
                        "_frame_index": field.get("_frame_index", 0),
                    }
                )

        return payload
