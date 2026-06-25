#!/usr/bin/env python3
"""
Refactor Sofiati footers across all concepts.

Goal:
- Same footer content order everywhere.
- Different footer colour, spacing, typography, icons, rhythm and atmosphere per concept.
- No boxes around footer columns.
- No repeated modulo footer template.
- Only touches each concept's footer partial and CSS footer block.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


CSS_START = "/* SOFIATI FOOTER V3 START */"
CSS_END = "/* SOFIATI FOOTER V3 END */"

MAIN_PAGES = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("care.html", "Care"),
    ("laser.html", "Laser"),
    ("skin.html", "Skin"),
    ("results.html", "Results"),
    ("consultation.html", "Consultation"),
    ("contact.html", "Contact"),
]

BRAND_TRUST = [
    ("mission.html", "Mission"),
    ("values.html", "Values"),
    ("testimonials.html", "Testimonials"),
    ("faq.html", "FAQ"),
    ("journal.html", "Journal"),
    ("blog.html", "Blog"),
]

LEGAL = [
    ("legal.html", "Legal"),
    ("privacy.html", "Privacy"),
    ("cookies.html", "Cookies"),
    ("accessibility.html", "Accessibility"),
    ("../../sitemap.xml", "Sitemap"),
]


@dataclass(frozen=True)
class FooterRecipe:
    number: int
    slug: str
    bg: str
    fg: str
    muted: str
    heading: str
    accent: str
    width: str
    columns: str
    pad_top: str
    pad_bottom: str
    column_gap: str
    row_gap: str
    link_gap: str
    heading_size: str
    heading_tracking: str
    link_size: str
    logo_width: str
    icon_style: str
    divider_style: str
    hover_style: str
    brand_align: str
    bottom_justify: str
    mobile_order: str
    dark_logo: bool


R = FooterRecipe


FOOTER_RECIPES: dict[int, FooterRecipe] = {
    1: R(1, "inspire", "linear-gradient(135deg,#252321,#354139)", "#F8F7F2", "rgba(248,247,242,.72)", "#F8F7F2", "#C9A56A", "min(1180px,calc(100% - 40px))", "minmax(270px,1.28fr) .72fr .86fr .68fr minmax(238px,1.08fr)", "clamp(34px,5vw,58px)", "clamp(30px,5vw,54px)", "clamp(28px,4vw,62px)", "22px", "7px", ".76rem", ".14em", ".94rem", "190px", "dot", "topline", "underline", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    2: R(2, "empower", "linear-gradient(90deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.68)", "#252321", "#879588", "min(1160px,calc(100% - 36px))", "minmax(250px,1.16fr) .78fr .92fr .7fr minmax(260px,1.2fr)", "clamp(38px,5vw,68px)", "clamp(30px,4vw,48px)", "clamp(24px,4vw,56px)", "18px", "9px", ".78rem", ".12em", ".96rem", "176px", "leaf", "leftline", "soft-shift", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    3: R(3, "enhance", "linear-gradient(180deg,#F4EFE5,#FBFAF6)", "#252321", "rgba(37,35,33,.66)", "#252321", "#9A6B35", "min(1120px,calc(100% - 32px))", "minmax(240px,1.08fr) .74fr .86fr .64fr minmax(230px,1fr)", "32px", "34px", "clamp(22px,3vw,44px)", "16px", "6px", ".72rem", ".16em", ".9rem", "164px", "ledger", "vertical-rules", "left-indent", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    4: R(4, "renew", "linear-gradient(135deg,#2B2B27,#405044)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#DAB26F", "min(1200px,calc(100% - 44px))", "minmax(260px,1.22fr) .76fr .88fr .68fr minmax(245px,1.12fr)", "clamp(36px,5vw,64px)", "clamp(34px,5vw,60px)", "clamp(26px,4vw,58px)", "20px", "8px", ".76rem", ".13em", ".94rem", "184px", "sprig", "soft-arc", "gold-sweep", "left", "center", '"brand" "pages" "trust" "contact" "legal" "bottom"', True),
    5: R(5, "elevate", "linear-gradient(135deg,#F4EFE5,#F8F7F2 58%,#E7D7BA)", "#252321", "rgba(37,35,33,.68)", "#252321", "#9A6B35", "min(1240px,calc(100% - 48px))", "minmax(290px,1.34fr) .7fr .82fr .64fr minmax(250px,1.08fr)", "clamp(42px,6vw,74px)", "clamp(34px,5vw,56px)", "clamp(30px,5vw,70px)", "24px", "7px", ".74rem", ".18em", ".94rem", "220px", "diamond", "champagne-rule", "opacity-lift", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    6: R(6, "refine", "#FBFBF8", "#252321", "rgba(37,35,33,.62)", "#252321", "#7F8D82", "min(1060px,calc(100% - 30px))", "minmax(230px,1.06fr) .72fr .8fr .64fr minmax(220px,1fr)", "28px", "30px", "clamp(20px,3vw,42px)", "14px", "5px", ".7rem", ".15em", ".88rem", "156px", "dash", "minimal", "underline", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    7: R(7, "glow", "radial-gradient(circle at 80% 20%,rgba(201,165,106,.16),transparent 34%),linear-gradient(180deg,#FFFFFF,#EFF3ED)", "#252321", "rgba(37,35,33,.66)", "#2E2B27", "#A2AEA0", "min(1180px,calc(100% - 38px))", "minmax(255px,1.12fr) .74fr .9fr .66fr minmax(250px,1.16fr)", "clamp(40px,6vw,72px)", "clamp(34px,5vw,58px)", "clamp(28px,4vw,64px)", "22px", "8px", ".75rem", ".14em", ".94rem", "188px", "circle", "glowline", "soft-shift", "left", "space-between", '"contact" "brand" "pages" "trust" "legal" "bottom"', False),
    8: R(8, "balance", "linear-gradient(180deg,#EEF1EA,#F8F7F2)", "#252321", "rgba(37,35,33,.68)", "#252321", "#879588", "min(1160px,calc(100% - 40px))", "minmax(252px,1.14fr) .8fr .8fr .68fr minmax(252px,1.14fr)", "36px", "36px", "clamp(26px,4vw,58px)", "20px", "8px", ".76rem", ".13em", ".94rem", "180px", "bracket", "balanced-rules", "underline", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    9: R(9, "radiance", "linear-gradient(135deg,#FFFDF8,#F4EFE5)", "#252321", "rgba(37,35,33,.64)", "#252321", "#C9A56A", "min(1220px,calc(100% - 42px))", "minmax(280px,1.25fr) .72fr .84fr .66fr minmax(240px,1.04fr)", "clamp(38px,5vw,66px)", "clamp(34px,5vw,54px)", "clamp(30px,5vw,66px)", "22px", "7px", ".74rem", ".16em", ".94rem", "200px", "sun", "topline", "gold-sweep", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    10: R(10, "essence", "#F8F7F2", "#252321", "rgba(37,35,33,.6)", "#252321", "#7F8D82", "min(980px,calc(100% - 28px))", "minmax(220px,1.08fr) .68fr .78fr .62fr minmax(210px,1fr)", "24px", "26px", "clamp(18px,3vw,36px)", "12px", "4px", ".68rem", ".12em", ".86rem", "148px", "none", "minimal", "opacity-lift", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    11: R(11, "bloom", "linear-gradient(135deg,#EAF0E8,#F8F7F2)", "#252321", "rgba(37,35,33,.66)", "#252321", "#879588", "min(1200px,calc(100% - 42px))", "minmax(270px,1.2fr) .72fr .86fr .66fr minmax(245px,1.1fr)", "clamp(40px,6vw,70px)", "clamp(34px,5vw,58px)", "clamp(28px,5vw,66px)", "22px", "8px", ".76rem", ".14em", ".94rem", "190px", "sprig", "organic-dots", "left-indent", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    12: R(12, "vital", "linear-gradient(135deg,#334339,#F8F7F2 38%,#F8F7F2)", "#252321", "rgba(37,35,33,.68)", "#252321", "#9A6B35", "min(1240px,calc(100% - 44px))", "minmax(255px,1.1fr) .74fr .88fr .66fr minmax(270px,1.2fr)", "clamp(34px,5vw,60px)", "clamp(32px,5vw,54px)", "clamp(24px,4vw,56px)", "18px", "8px", ".76rem", ".13em", ".94rem", "178px", "arrow", "motion-line", "left-indent", "left", "space-between", '"brand" "pages" "trust" "contact" "legal" "bottom"', False),
    13: R(13, "poise", "linear-gradient(180deg,#252321,#313833)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#C9A56A", "min(1160px,calc(100% - 38px))", "minmax(270px,1.3fr) .7fr .82fr .64fr minmax(230px,1.02fr)", "clamp(38px,5vw,64px)", "clamp(32px,5vw,52px)", "clamp(30px,5vw,68px)", "20px", "7px", ".74rem", ".18em", ".92rem", "204px", "diamond", "editorial-rule", "underline", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    14: R(14, "aura", "radial-gradient(circle at 70% 18%,rgba(201,165,106,.18),transparent 40%),linear-gradient(135deg,#EEF1EA,#FFFFFF)", "#252321", "rgba(37,35,33,.64)", "#252321", "#C9A56A", "min(1180px,calc(100% - 40px))", "minmax(260px,1.16fr) .74fr .86fr .66fr minmax(250px,1.12fr)", "clamp(42px,6vw,76px)", "clamp(36px,5vw,60px)", "clamp(28px,5vw,68px)", "24px", "9px", ".76rem", ".12em", ".96rem", "196px", "halo", "glowline", "soft-shift", "center", "center", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    15: R(15, "clarity", "#FFFFFF", "#252321", "rgba(37,35,33,.66)", "#252321", "#7F8D82", "min(1120px,calc(100% - 32px))", "minmax(240px,1.08fr) .74fr .88fr .68fr minmax(238px,1.08fr)", "30px", "32px", "clamp(22px,3vw,46px)", "16px", "6px", ".72rem", ".16em", ".9rem", "166px", "ledger", "vertical-rules", "underline", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    16: R(16, "grace", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.66)", "#252321", "#A2AEA0", "min(1160px,calc(100% - 38px))", "minmax(258px,1.16fr) .72fr .86fr .66fr minmax(246px,1.08fr)", "clamp(38px,5vw,66px)", "clamp(32px,5vw,54px)", "clamp(28px,4vw,60px)", "20px", "8px", ".75rem", ".13em", ".94rem", "184px", "curve", "soft-arc", "opacity-lift", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    17: R(17, "sculpt", "linear-gradient(135deg,#252321,#3D372F)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#C9A56A", "min(1220px,calc(100% - 42px))", "minmax(275px,1.28fr) .68fr .86fr .64fr minmax(245px,1.1fr)", "clamp(36px,5vw,62px)", "clamp(32px,5vw,54px)", "clamp(30px,5vw,68px)", "20px", "8px", ".76rem", ".14em", ".94rem", "198px", "angle", "diagonal", "left-indent", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', True),
    18: R(18, "lumin", "linear-gradient(135deg,#FFFFFF,#EEF3EE 62%,#E7D7BA)", "#252321", "rgba(37,35,33,.62)", "#252321", "#C9A56A", "min(1180px,calc(100% - 40px))", "minmax(255px,1.14fr) .74fr .86fr .66fr minmax(255px,1.16fr)", "clamp(42px,6vw,72px)", "clamp(34px,5vw,58px)", "clamp(28px,5vw,64px)", "22px", "8px", ".74rem", ".14em", ".94rem", "192px", "ray", "glowline", "gold-sweep", "left", "space-between", '"contact" "brand" "pages" "trust" "legal" "bottom"', False),
    19: R(19, "verda", "linear-gradient(135deg,#2E3A32,#506052)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#DAB26F", "min(1200px,calc(100% - 44px))", "minmax(270px,1.22fr) .72fr .88fr .68fr minmax(246px,1.1fr)", "clamp(40px,5vw,68px)", "clamp(34px,5vw,58px)", "clamp(28px,5vw,66px)", "22px", "8px", ".76rem", ".14em", ".94rem", "194px", "sprig", "organic-dots", "soft-shift", "left", "space-between", '"brand" "pages" "trust" "contact" "legal" "bottom"', True),
    20: R(20, "halo", "radial-gradient(circle at 50% 20%,rgba(201,165,106,.16),transparent 36%),linear-gradient(180deg,#252321,#334139)", "#F8F7F2", "rgba(248,247,242,.72)", "#F8F7F2", "#C9A56A", "min(1160px,calc(100% - 40px))", "minmax(260px,1.2fr) .7fr .84fr .66fr minmax(240px,1.08fr)", "clamp(38px,5vw,64px)", "clamp(32px,5vw,54px)", "clamp(26px,4vw,58px)", "20px", "8px", ".75rem", ".13em", ".94rem", "186px", "halo", "centerline", "underline", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    21: R(21, "calm", "#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#252321", "#A2AEA0", "min(1040px,calc(100% - 30px))", "minmax(230px,1.04fr) .72fr .82fr .64fr minmax(220px,1fr)", "28px", "30px", "clamp(20px,3vw,40px)", "14px", "6px", ".7rem", ".12em", ".88rem", "156px", "dash", "minimal", "opacity-lift", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    22: R(22, "precision", "#FFFFFF", "#252321", "rgba(37,35,33,.66)", "#252321", "#7F8D82", "min(1120px,calc(100% - 32px))", "minmax(245px,1.08fr) .72fr .9fr .68fr minmax(238px,1.08fr)", "30px", "32px", "clamp(20px,3vw,42px)", "16px", "5px", ".68rem", ".18em", ".88rem", "162px", "ledger", "vertical-rules", "left-indent", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    23: R(23, "ritual", "linear-gradient(180deg,#F4EFE5,#FBFAF6)", "#252321", "rgba(37,35,33,.66)", "#252321", "#9A6B35", "min(1140px,calc(100% - 34px))", "minmax(250px,1.12fr) .74fr .84fr .66fr minmax(235px,1.04fr)", "clamp(34px,5vw,60px)", "clamp(32px,5vw,52px)", "clamp(24px,4vw,54px)", "18px", "8px", ".74rem", ".15em", ".92rem", "176px", "step", "champagne-rule", "gold-sweep", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    24: R(24, "signal", "linear-gradient(135deg,#202524,#313A35)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#A2AEA0", "min(1200px,calc(100% - 40px))", "minmax(255px,1.14fr) .74fr .9fr .68fr minmax(250px,1.14fr)", "32px", "34px", "clamp(22px,4vw,54px)", "18px", "7px", ".72rem", ".16em", ".9rem", "172px", "signal", "scanline", "soft-shift", "left", "space-between", '"contact" "brand" "pages" "trust" "legal" "bottom"', True),
    25: R(25, "align", "#FBFBF8", "#252321", "rgba(37,35,33,.66)", "#252321", "#879588", "min(1180px,calc(100% - 38px))", "minmax(255px,1.14fr) .76fr .88fr .68fr minmax(245px,1.1fr)", "32px", "34px", "clamp(24px,4vw,56px)", "18px", "6px", ".72rem", ".14em", ".9rem", "174px", "line", "balanced-rules", "underline", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    26: R(26, "vivant", "linear-gradient(135deg,#EEF1EA,#FFFFFF 55%,#F4EFE5)", "#252321", "rgba(37,35,33,.64)", "#252321", "#9A6B35", "min(1220px,calc(100% - 42px))", "minmax(260px,1.16fr) .74fr .86fr .66fr minmax(260px,1.18fr)", "clamp(38px,5vw,68px)", "clamp(34px,5vw,56px)", "clamp(28px,5vw,64px)", "22px", "8px", ".76rem", ".12em", ".95rem", "190px", "arrow", "motion-line", "left-indent", "left", "space-between", '"brand" "pages" "trust" "contact" "legal" "bottom"', False),
    27: R(27, "form", "linear-gradient(135deg,#2B2B27,#40382F)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#C9A56A", "min(1180px,calc(100% - 40px))", "minmax(265px,1.22fr) .7fr .84fr .66fr minmax(240px,1.08fr)", "clamp(34px,5vw,60px)", "clamp(32px,5vw,54px)", "clamp(26px,4vw,58px)", "18px", "7px", ".74rem", ".15em", ".92rem", "186px", "angle", "diagonal", "underline", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', True),
    28: R(28, "pure", "#FFFFFF", "#252321", "rgba(37,35,33,.58)", "#252321", "#A2AEA0", "min(980px,calc(100% - 28px))", "minmax(220px,1.06fr) .7fr .78fr .62fr minmax(215px,1fr)", "24px", "26px", "clamp(18px,3vw,34px)", "12px", "5px", ".68rem", ".13em", ".86rem", "146px", "none", "minimal", "opacity-lift", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    29: R(29, "solace", "linear-gradient(180deg,#F8F7F2,#F0EEE5)", "#252321", "rgba(37,35,33,.64)", "#252321", "#879588", "min(1120px,calc(100% - 34px))", "minmax(248px,1.1fr) .72fr .84fr .66fr minmax(250px,1.16fr)", "clamp(34px,5vw,60px)", "clamp(32px,5vw,52px)", "clamp(24px,4vw,52px)", "18px", "9px", ".74rem", ".12em", ".94rem", "176px", "circle", "soft-arc", "soft-shift", "left", "space-between", '"contact" "brand" "pages" "trust" "legal" "bottom"', False),
    30: R(30, "method", "#FBFAF6", "#252321", "rgba(37,35,33,.66)", "#252321", "#9A6B35", "min(1140px,calc(100% - 32px))", "minmax(250px,1.1fr) .74fr .88fr .66fr minmax(240px,1.08fr)", "30px", "32px", "clamp(22px,3vw,46px)", "16px", "6px", ".7rem", ".17em", ".9rem", "168px", "step", "vertical-rules", "left-indent", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    31: R(31, "evolve", "linear-gradient(135deg,#EEF1EA,#F8F7F2 60%,#E7D7BA)", "#252321", "rgba(37,35,33,.66)", "#252321", "#9A6B35", "min(1200px,calc(100% - 40px))", "minmax(260px,1.16fr) .72fr .86fr .66fr minmax(250px,1.12fr)", "clamp(38px,5vw,66px)", "clamp(34px,5vw,56px)", "clamp(28px,4vw,60px)", "22px", "8px", ".75rem", ".13em", ".94rem", "186px", "arrow", "motion-line", "gold-sweep", "left", "space-between", '"brand" "pages" "trust" "contact" "legal" "bottom"', False),
    32: R(32, "serene", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.62)", "#252321", "#A2AEA0", "min(1080px,calc(100% - 32px))", "minmax(240px,1.08fr) .72fr .82fr .64fr minmax(230px,1.02fr)", "clamp(34px,5vw,58px)", "clamp(30px,5vw,50px)", "clamp(24px,4vw,52px)", "18px", "7px", ".72rem", ".12em", ".9rem", "170px", "dash", "soft-arc", "opacity-lift", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    33: R(33, "elan", "linear-gradient(135deg,#252321,#2E3A32)", "#F8F7F2", "rgba(248,247,242,.72)", "#F8F7F2", "#C9A56A", "min(1240px,calc(100% - 44px))", "minmax(285px,1.34fr) .7fr .86fr .66fr minmax(240px,1.06fr)", "clamp(40px,6vw,72px)", "clamp(34px,5vw,58px)", "clamp(30px,5vw,70px)", "22px", "7px", ".76rem", ".18em", ".94rem", "214px", "diamond", "editorial-rule", "gold-sweep", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    34: R(34, "flora", "linear-gradient(135deg,#E9F0E6,#F8F7F2)", "#252321", "rgba(37,35,33,.66)", "#252321", "#879588", "min(1200px,calc(100% - 42px))", "minmax(265px,1.18fr) .72fr .86fr .66fr minmax(250px,1.14fr)", "clamp(40px,6vw,70px)", "clamp(34px,5vw,56px)", "clamp(28px,5vw,66px)", "22px", "8px", ".76rem", ".14em", ".94rem", "190px", "sprig", "organic-dots", "soft-shift", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    35: R(35, "atelier", "#FBFAF6", "#252321", "rgba(37,35,33,.64)", "#252321", "#9A6B35", "min(1220px,calc(100% - 44px))", "minmax(280px,1.26fr) .72fr .86fr .66fr minmax(240px,1.04fr)", "clamp(38px,5vw,66px)", "clamp(32px,5vw,54px)", "clamp(30px,5vw,68px)", "22px", "7px", ".74rem", ".18em", ".94rem", "206px", "bracket", "editorial-rule", "underline", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    36: R(36, "lumina", "radial-gradient(circle at 70% 22%,rgba(201,165,106,.18),transparent 36%),linear-gradient(135deg,#FFFFFF,#EEF3ED)", "#252321", "rgba(37,35,33,.62)", "#252321", "#C9A56A", "min(1180px,calc(100% - 40px))", "minmax(258px,1.14fr) .72fr .86fr .66fr minmax(250px,1.12fr)", "clamp(42px,6vw,74px)", "clamp(34px,5vw,58px)", "clamp(28px,4vw,62px)", "22px", "8px", ".75rem", ".13em", ".94rem", "194px", "ray", "glowline", "soft-shift", "left", "space-between", '"contact" "brand" "pages" "trust" "legal" "bottom"', False),
    37: R(37, "vellum", "linear-gradient(180deg,#FBFAF6,#F4EFE5)", "#252321", "rgba(37,35,33,.66)", "#252321", "#9A6B35", "min(1100px,calc(100% - 32px))", "minmax(245px,1.1fr) .74fr .88fr .66fr minmax(230px,1.04fr)", "32px", "34px", "clamp(22px,3vw,46px)", "16px", "6px", ".7rem", ".16em", ".9rem", "166px", "ledger", "paper-rule", "underline", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    38: R(38, "origin", "linear-gradient(135deg,#2B312D,#445044)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#C9A56A", "min(1180px,calc(100% - 40px))", "minmax(270px,1.24fr) .72fr .86fr .66fr minmax(240px,1.06fr)", "clamp(36px,5vw,62px)", "clamp(32px,5vw,54px)", "clamp(28px,5vw,64px)", "20px", "7px", ".74rem", ".14em", ".92rem", "192px", "root", "leftline", "opacity-lift", "left", "space-between", '"brand" "pages" "trust" "contact" "legal" "bottom"', True),
    39: R(39, "kindred", "linear-gradient(180deg,#F8F7F2,#F1EEE7)", "#252321", "rgba(37,35,33,.66)", "#252321", "#A2AEA0", "min(1160px,calc(100% - 36px))", "minmax(255px,1.12fr) .72fr .84fr .66fr minmax(260px,1.18fr)", "clamp(36px,5vw,62px)", "clamp(32px,5vw,54px)", "clamp(24px,4vw,56px)", "20px", "8px", ".74rem", ".12em", ".94rem", "180px", "circle", "soft-arc", "soft-shift", "left", "space-between", '"contact" "brand" "pages" "trust" "legal" "bottom"', False),
    40: R(40, "noble", "linear-gradient(135deg,#201F1E,#302A23)", "#F8F7F2", "rgba(248,247,242,.72)", "#F8F7F2", "#DAB26F", "min(1220px,calc(100% - 44px))", "minmax(285px,1.34fr) .7fr .84fr .66fr minmax(240px,1.06fr)", "clamp(40px,6vw,72px)", "clamp(34px,5vw,56px)", "clamp(32px,5vw,72px)", "22px", "7px", ".74rem", ".2em", ".94rem", "218px", "diamond", "champagne-rule", "gold-sweep", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    41: R(41, "vista", "linear-gradient(90deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.66)", "#252321", "#879588", "min(1320px,calc(100% - 50px))", "minmax(300px,1.34fr) .72fr .86fr .66fr minmax(260px,1.08fr)", "clamp(34px,5vw,58px)", "clamp(32px,5vw,52px)", "clamp(34px,5vw,78px)", "18px", "7px", ".74rem", ".15em", ".94rem", "202px", "horizon", "wide-rule", "left-indent", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    42: R(42, "softline", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.64)", "#252321", "#A2AEA0", "min(1160px,calc(100% - 38px))", "minmax(252px,1.12fr) .74fr .84fr .66fr minmax(244px,1.08fr)", "clamp(36px,5vw,64px)", "clamp(32px,5vw,54px)", "clamp(26px,4vw,58px)", "20px", "8px", ".74rem", ".13em", ".94rem", "182px", "curve", "soft-arc", "underline", "center", "center", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    43: R(43, "meridian", "#FBFBF8", "#252321", "rgba(37,35,33,.66)", "#252321", "#879588", "min(1180px,calc(100% - 36px))", "minmax(255px,1.16fr) .74fr .88fr .66fr minmax(245px,1.1fr)", "32px", "34px", "clamp(24px,4vw,56px)", "18px", "6px", ".72rem", ".16em", ".9rem", "172px", "compass", "centerline", "left-indent", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    44: R(44, "safeguard", "#FFFFFF", "#252321", "rgba(37,35,33,.7)", "#252321", "#7F8D82", "min(1100px,calc(100% - 32px))", "minmax(245px,1.1fr) .74fr .86fr .66fr minmax(238px,1.08fr)", "30px", "32px", "clamp(22px,3vw,46px)", "16px", "7px", ".72rem", ".16em", ".92rem", "166px", "shield", "vertical-rules", "underline", "left", "space-between", '"brand" "contact" "pages" "trust" "legal" "bottom"', False),
    45: R(45, "silhouette", "linear-gradient(135deg,#252321,#354139)", "#F8F7F2", "rgba(248,247,242,.68)", "#F8F7F2", "#C9A56A", "min(1160px,calc(100% - 38px))", "minmax(265px,1.18fr) .72fr .84fr .66fr minmax(240px,1.08fr)", "clamp(34px,5vw,60px)", "clamp(32px,5vw,54px)", "clamp(28px,4vw,60px)", "20px", "7px", ".74rem", ".14em", ".92rem", "188px", "silhouette", "minimal", "opacity-lift", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    46: R(46, "curate", "linear-gradient(135deg,#F4EFE5,#FFFFFF)", "#252321", "rgba(37,35,33,.64)", "#252321", "#9A6B35", "min(1200px,calc(100% - 42px))", "minmax(275px,1.24fr) .72fr .86fr .66fr minmax(245px,1.08fr)", "clamp(36px,5vw,62px)", "clamp(32px,5vw,54px)", "clamp(28px,5vw,64px)", "20px", "8px", ".74rem", ".15em", ".94rem", "194px", "bracket", "champagne-rule", "gold-sweep", "left", "space-between", '"brand" "pages" "trust" "contact" "legal" "bottom"', False),
    47: R(47, "proof", "#FBFBF8", "#252321", "rgba(37,35,33,.68)", "#252321", "#7F8D82", "min(1120px,calc(100% - 32px))", "minmax(250px,1.12fr) .74fr .9fr .68fr minmax(235px,1.04fr)", "30px", "32px", "clamp(22px,3vw,46px)", "16px", "6px", ".7rem", ".18em", ".9rem", "166px", "check", "vertical-rules", "left-indent", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    48: R(48, "signature", "linear-gradient(180deg,#F8F7F2,#F4EFE5)", "#252321", "rgba(37,35,33,.64)", "#252321", "#9A6B35", "min(1220px,calc(100% - 44px))", "minmax(300px,1.38fr) .7fr .82fr .64fr minmax(235px,1.02fr)", "clamp(40px,6vw,72px)", "clamp(34px,5vw,56px)", "clamp(32px,5vw,72px)", "22px", "7px", ".74rem", ".18em", ".94rem", "230px", "signature", "editorial-rule", "underline", "center", "center", '"brand" "pages" "trust" "legal" "contact" "bottom"', False),
    49: R(49, "wisdom", "linear-gradient(135deg,#252321,#313833)", "#F8F7F2", "rgba(248,247,242,.7)", "#F8F7F2", "#C9A56A", "min(1180px,calc(100% - 38px))", "minmax(270px,1.24fr) .72fr .9fr .66fr minmax(235px,1.04fr)", "clamp(36px,5vw,64px)", "clamp(32px,5vw,54px)", "clamp(28px,5vw,64px)", "20px", "8px", ".74rem", ".16em", ".92rem", "196px", "book", "paper-rule", "soft-shift", "left", "space-between", '"brand" "pages" "trust" "legal" "contact" "bottom"', True),
    50: R(50, "sovereign", "linear-gradient(135deg,#1F1E1D,#334139 58%,#9A6B35)", "#F8F7F2", "rgba(248,247,242,.72)", "#F8F7F2", "#DAB26F", "min(1280px,calc(100% - 48px))", "minmax(310px,1.42fr) .72fr .88fr .66fr minmax(255px,1.12fr)", "clamp(44px,6vw,78px)", "clamp(36px,5vw,62px)", "clamp(34px,5vw,78px)", "24px", "8px", ".76rem", ".2em", ".96rem", "238px", "crest", "champagne-rule", "gold-sweep", "center", "center", '"brand" "contact" "pages" "trust" "legal" "bottom"', True),
}


def concept_dirs(concepts_dir: Path) -> list[Path]:
    if not concepts_dir.exists():
        raise FileNotFoundError(f"Missing concepts directory: {concepts_dir}")
    return sorted(
        p for p in concepts_dir.iterdir()
        if p.is_dir() and re.match(r"^\d{2}-", p.name)
    )


def concept_number(concept: Path) -> int:
    return int(concept.name.split("-", 1)[0])


def find_css_file(concept: Path) -> Path:
    candidates = [
        concept / "assets" / "css" / "style.css",
        concept / "css" / "style.css",
        concept / "style.css",
        concept / "assets" / "style.css",
    ]
    for path in candidates:
        if path.exists():
            return path

    # Prefer creating this path if none exists.
    path = concept / "assets" / "css" / "style.css"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def logo_src(recipe: FooterRecipe) -> str:
    if recipe.dark_logo:
        return "assets/brand/sofiati-logo-primary-white.png"
    return "assets/brand/sofiati-logo-primary-sage.png"


def monogram_src(recipe: FooterRecipe) -> str:
    if recipe.dark_logo:
        return "assets/brand/sofiati-monogram-white.png"
    return "assets/brand/sofiati-monogram-sage.png"


def render_links(items: list[tuple[str, str]]) -> str:
    return "\n".join(f'      <a href="{href}">{label}</a>' for href, label in items)


def render_footer_group(title: str, items: list[tuple[str, str]], class_name: str) -> str:
    return f'''    <nav class="footer-link-group {class_name}" aria-label="{title}">
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>{title}</h3>
{render_links(items)}
    </nav>'''


def render_footer_html(recipe: FooterRecipe, code: str) -> str:
    return f'''<footer class="site-footer public-footer public-footer-{code} public-footer-recipe-{recipe.slug} public-footer-icons-{recipe.icon_style} public-footer-divider-{recipe.divider_style} public-footer-hover-{recipe.hover_style}" data-footer-recipe="{recipe.slug}">
  <div class="public-footer-shell">
    <section class="footer-brand-panel" aria-label="Brand">
      <a class="footer-signature-logo" href="index.html" aria-label="Sofiati home">
        <img src="{logo_src(recipe)}" alt="Franciele Sofiati signature logo">
      </a>
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>Brand</h3>
      <h2>Franciele Sofiati</h2>
      <p class="footer-role">Advanced Aesthetic Biomedicine</p>
      <p class="footer-credential">CRBM 6277</p>
      <p class="footer-description">Laser and skin care guided by professional evaluation in Londrina, PR.</p>
      <a class="footer-cta" href="consultation.html">Consultation</a>
    </section>

{render_footer_group("Main Pages", MAIN_PAGES, "footer-main-links")}

{render_footer_group("Brand and Trust", BRAND_TRUST, "footer-trust-links")}

{render_footer_group("Legal", LEGAL, "footer-legal-links")}

    <address class="footer-contact" aria-label="Contact">
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>Contact</h3>
      <a href="https://wa.me/5543991043536" rel="noopener" target="_blank">WhatsApp: (43) 9 9104-3536</a>
      <a href="mailto:sofiatimendonca@gmail.com">sofiatimendonca@gmail.com</a>
      <a href="https://www.instagram.com/fransofiati_biomedica/" rel="noopener" target="_blank">@fransofiati_biomedica</a>
      <span>Londrina, PR</span>
    </address>

    <div class="footer-bottom-row">
      <p>Information on this website is educational and does not replace an individual professional evaluation.</p>
      <p>© 2026 Franciele Sofiati. All rights reserved.</p>
    </div>
  </div>
</footer>
'''


def render_footer_css(recipe: FooterRecipe, code: str) -> str:
    return f'''
{CSS_START}
.public-footer {{
  --footer-bg: #252321;
  --footer-fg: #F8F7F2;
  --footer-muted: rgba(248,247,242,.72);
  --footer-heading: #F8F7F2;
  --footer-accent: #C9A56A;
  --footer-link-hover: var(--footer-accent);

  position: relative;
  isolation: isolate;
  overflow: hidden;
  margin-top: clamp(32px, 5vw, 72px);
  background: var(--footer-bg);
  color: var(--footer-fg);
}}

.public-footer,
.public-footer * {{
  box-sizing: border-box;
}}

.public-footer::before,
.public-footer::after {{
  content: "";
  position: absolute;
  pointer-events: none;
  z-index: 0;
}}

.public-footer-shell {{
  position: relative;
  z-index: 1;
  width: var(--footer-width);
  margin-inline: auto;
  display: grid;
  grid-template-columns: var(--footer-columns);
  grid-template-areas:
    "brand pages trust legal contact"
    "bottom bottom bottom bottom bottom";
  gap: var(--footer-row-gap) var(--footer-column-gap);
  padding-block: var(--footer-pad-top) var(--footer-pad-bottom);
}}

.footer-brand-panel {{ grid-area: brand; }}
.footer-main-links {{ grid-area: pages; }}
.footer-trust-links {{ grid-area: trust; }}
.footer-legal-links {{ grid-area: legal; }}
.footer-contact {{ grid-area: contact; }}
.footer-bottom-row {{ grid-area: bottom; }}

.footer-brand-panel,
.footer-link-group,
.footer-contact {{
  display: grid;
  align-content: start;
  gap: var(--footer-link-gap);
  min-height: 0;
  padding: 0;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}}

.footer-brand-panel {{
  justify-items: var(--footer-brand-align);
  text-align: var(--footer-brand-align);
}}

.footer-signature-logo {{
  display: inline-flex;
  width: fit-content;
  margin: 0 0 8px;
  text-decoration: none;
}}

.footer-signature-logo img {{
  width: var(--footer-logo-width);
  max-width: min(72vw, var(--footer-logo-width));
  max-height: 84px;
  object-fit: contain;
  display: block;
}}

.footer-brand-panel h2 {{
  margin: 2px 0 0;
  color: var(--footer-fg);
  font-size: clamp(1.45rem, 2.2vw, 2.55rem);
  line-height: 1.04;
  letter-spacing: -.02em;
}}

.footer-role,
.footer-credential {{
  margin: 0;
  color: var(--footer-fg);
  font-weight: 800;
  line-height: 1.35;
}}

.footer-description {{
  max-width: 30ch;
  margin: 2px 0 0;
  color: var(--footer-muted);
  font-size: var(--footer-link-size);
  line-height: 1.5;
}}

.footer-link-group h3,
.footer-contact h3,
.footer-brand-panel h3 {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  margin: 0 0 8px;
  color: var(--footer-heading);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  font-size: var(--footer-heading-size);
  font-weight: 900;
  letter-spacing: var(--footer-heading-tracking);
  line-height: 1.15;
  text-transform: uppercase;
}}

.footer-heading-icon {{
  width: 12px;
  height: 12px;
  display: inline-block;
  color: var(--footer-accent);
  flex: 0 0 auto;
  position: relative;
}}

.public-footer-icons-none .footer-heading-icon {{
  display: none;
}}

.public-footer-icons-dot .footer-heading-icon,
.public-footer-icons-circle .footer-heading-icon,
.public-footer-icons-halo .footer-heading-icon {{
  border: 1px solid currentColor;
  border-radius: 999px;
}}

.public-footer-icons-dot .footer-heading-icon::after {{
  content: "";
  position: absolute;
  inset: 3px;
  border-radius: 999px;
  background: currentColor;
}}

.public-footer-icons-leaf .footer-heading-icon,
.public-footer-icons-sprig .footer-heading-icon {{
  width: 14px;
  height: 8px;
  border: 1px solid currentColor;
  border-left: 0;
  border-radius: 100% 0 100% 0;
  transform: rotate(-24deg);
}}

.public-footer-icons-ledger .footer-heading-icon,
.public-footer-icons-line .footer-heading-icon,
.public-footer-icons-dash .footer-heading-icon {{
  width: 16px;
  height: 1px;
  background: currentColor;
}}

.public-footer-icons-diamond .footer-heading-icon {{
  width: 9px;
  height: 9px;
  border: 1px solid currentColor;
  transform: rotate(45deg);
}}

.public-footer-icons-bracket .footer-heading-icon {{
  width: 10px;
  height: 12px;
  border-left: 1px solid currentColor;
  border-top: 1px solid currentColor;
  border-bottom: 1px solid currentColor;
}}

.public-footer-icons-arrow .footer-heading-icon::before,
.public-footer-icons-step .footer-heading-icon::before,
.public-footer-icons-signal .footer-heading-icon::before,
.public-footer-icons-ray .footer-heading-icon::before,
.public-footer-icons-angle .footer-heading-icon::before,
.public-footer-icons-root .footer-heading-icon::before,
.public-footer-icons-compass .footer-heading-icon::before,
.public-footer-icons-shield .footer-heading-icon::before,
.public-footer-icons-silhouette .footer-heading-icon::before,
.public-footer-icons-signature .footer-heading-icon::before,
.public-footer-icons-book .footer-heading-icon::before,
.public-footer-icons-crest .footer-heading-icon::before,
.public-footer-icons-horizon .footer-heading-icon::before,
.public-footer-icons-sun .footer-heading-icon::before,
.public-footer-icons-curve .footer-heading-icon::before,
.public-footer-icons-check .footer-heading-icon::before {{
  content: "";
  position: absolute;
  inset: 2px;
  border-top: 1px solid currentColor;
  border-right: 1px solid currentColor;
  transform: rotate(45deg);
}}

.public-footer-icons-check .footer-heading-icon::before {{
  inset: 1px 3px 3px 2px;
  border-top: 0;
  transform: rotate(40deg);
}}

.footer-link-group a,
.footer-contact a,
.footer-contact span {{
  min-height: 28px;
  display: flex;
  align-items: center;
  width: fit-content;
  color: var(--footer-muted);
  font-size: var(--footer-link-size);
  line-height: 1.35;
  text-decoration: none;
  transition:
    color .2s ease,
    opacity .2s ease,
    transform .2s ease,
    text-decoration-color .2s ease;
}}

.footer-contact {{
  font-style: normal;
}}

.footer-link-group a:hover,
.footer-contact a:hover {{
  color: var(--footer-link-hover);
}}

.public-footer-hover-underline .footer-link-group a:hover,
.public-footer-hover-underline .footer-contact a:hover {{
  text-decoration: underline;
  text-underline-offset: .28em;
}}

.public-footer-hover-left-indent .footer-link-group a:hover,
.public-footer-hover-left-indent .footer-contact a:hover {{
  transform: translateX(4px);
}}

.public-footer-hover-opacity-lift .footer-link-group a,
.public-footer-hover-opacity-lift .footer-contact a {{
  opacity: .82;
}}

.public-footer-hover-opacity-lift .footer-link-group a:hover,
.public-footer-hover-opacity-lift .footer-contact a:hover {{
  opacity: 1;
}}

.public-footer-hover-gold-sweep .footer-link-group a,
.public-footer-hover-gold-sweep .footer-contact a {{
  background-image: linear-gradient(var(--footer-accent), var(--footer-accent));
  background-size: 0 1px;
  background-position: 0 100%;
  background-repeat: no-repeat;
}}

.public-footer-hover-gold-sweep .footer-link-group a:hover,
.public-footer-hover-gold-sweep .footer-contact a:hover {{
  background-size: 100% 1px;
}}

.public-footer-hover-soft-shift .footer-link-group a:hover,
.public-footer-hover-soft-shift .footer-contact a:hover {{
  color: var(--footer-fg);
}}

.footer-cta {{
  justify-self: var(--footer-brand-align);
  width: fit-content;
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 6px;
  padding: 8px 14px;
  border: 1px solid color-mix(in srgb, var(--footer-accent) 52%, transparent);
  border-radius: 999px;
  color: var(--footer-fg);
  background: color-mix(in srgb, var(--footer-accent) 16%, transparent);
  text-decoration: none;
  font-size: .92rem;
  font-weight: 850;
}}

.footer-bottom-row {{
  display: flex;
  justify-content: var(--footer-bottom-justify);
  gap: 12px 28px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid color-mix(in srgb, var(--footer-accent) 34%, transparent);
}}

.footer-bottom-row p {{
  max-width: 78ch;
  margin: 0;
  color: var(--footer-muted);
  font-size: clamp(.82rem, .78vw, .9rem);
  line-height: 1.45;
}}

.public-footer-divider-topline::before {{
  inset: 0 0 auto;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--footer-accent), transparent);
}}

.public-footer-divider-leftline::before,
.public-footer-divider-vertical-rules::before {{
  left: clamp(18px, 4vw, 68px);
  top: 22px;
  width: 1px;
  height: calc(100% - 44px);
  background: linear-gradient(180deg, transparent, color-mix(in srgb, var(--footer-accent) 52%, transparent), transparent);
}}

.public-footer-divider-champagne-rule::before,
.public-footer-divider-editorial-rule::before,
.public-footer-divider-wide-rule::before,
.public-footer-divider-centerline::before,
.public-footer-divider-paper-rule::before {{
  left: clamp(22px, 5vw, 90px);
  right: clamp(22px, 5vw, 90px);
  top: 18px;
  height: 1px;
  background: linear-gradient(90deg, var(--footer-accent), transparent, var(--footer-accent));
  opacity: .62;
}}

.public-footer-divider-glowline::before {{
  inset: 0;
  background: radial-gradient(circle at 74% 18%, color-mix(in srgb, var(--footer-accent) 14%, transparent), transparent 40%);
}}

.public-footer-divider-soft-arc::before {{
  right: clamp(28px, 7vw, 120px);
  top: 24px;
  width: 64px;
  height: 64px;
  border: 1px solid color-mix(in srgb, var(--footer-accent) 42%, transparent);
  border-radius: 999px;
  opacity: .65;
}}

.public-footer-divider-organic-dots::before {{
  right: clamp(26px, 8vw, 130px);
  top: 28px;
  width: 74px;
  height: 28px;
  background:
    radial-gradient(circle, var(--footer-accent) 0 2px, transparent 3px) 0 0 / 18px 18px;
  opacity: .36;
}}

.public-footer-divider-motion-line::before {{
  left: 0;
  right: 0;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0 12%, var(--footer-accent) 28%, transparent 44%, var(--footer-accent) 72%, transparent);
  opacity: .62;
}}

.public-footer-divider-diagonal::before {{
  right: clamp(24px, 5vw, 80px);
  top: 0;
  width: 1px;
  height: 100%;
  background: color-mix(in srgb, var(--footer-accent) 28%, transparent);
  transform: rotate(8deg);
  transform-origin: top;
}}

.public-footer-divider-scanline::before {{
  inset: 0;
  background: repeating-linear-gradient(180deg, color-mix(in srgb, var(--footer-accent) 10%, transparent) 0 1px, transparent 1px 18px);
  opacity: .22;
}}

.public-footer-{code} {{
  --footer-bg: {recipe.bg};
  --footer-fg: {recipe.fg};
  --footer-muted: {recipe.muted};
  --footer-heading: {recipe.heading};
  --footer-accent: {recipe.accent};
  --footer-link-hover: {recipe.accent};
  --footer-width: {recipe.width};
  --footer-columns: {recipe.columns};
  --footer-pad-top: {recipe.pad_top};
  --footer-pad-bottom: {recipe.pad_bottom};
  --footer-column-gap: {recipe.column_gap};
  --footer-row-gap: {recipe.row_gap};
  --footer-link-gap: {recipe.link_gap};
  --footer-heading-size: {recipe.heading_size};
  --footer-heading-tracking: {recipe.heading_tracking};
  --footer-link-size: {recipe.link_size};
  --footer-logo-width: {recipe.logo_width};
  --footer-brand-align: {recipe.brand_align};
  --footer-bottom-justify: {recipe.bottom_justify};
}}

@media (max-width: 980px) {{
  .public-footer-shell {{
    width: min(760px, calc(100% - 30px));
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "brand contact"
      "pages trust"
      "legal legal"
      "bottom bottom";
    gap: 22px 28px;
    padding-block: 32px 38px;
  }}

  .footer-brand-panel {{
    justify-items: start;
    text-align: left;
  }}
}}

@media (max-width: 620px) {{
  .public-footer {{
    margin-top: 34px;
  }}

  .public-footer-shell {{
    width: min(520px, calc(100% - 28px));
    grid-template-columns: 1fr;
    grid-template-areas: {recipe.mobile_order};
    gap: 16px;
    padding-block: 28px 32px;
  }}

  .footer-brand-panel,
  .footer-link-group,
  .footer-contact {{
    justify-items: start;
    text-align: left;
  }}

  .footer-signature-logo img {{
    width: min(168px, 62vw);
    max-height: 58px;
  }}

  .footer-brand-panel h2 {{
    font-size: clamp(1.3rem, 7vw, 1.85rem);
  }}

  .footer-link-group {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 4px 14px;
  }}

  .footer-link-group h3 {{
    grid-column: 1 / -1;
    margin-bottom: 2px;
  }}

  .footer-link-group a,
  .footer-contact a,
  .footer-contact span {{
    min-height: 32px;
    font-size: .9rem;
  }}

  .footer-bottom-row {{
    display: grid;
    justify-content: start;
    padding-top: 12px;
  }}

  .public-footer::before,
  .public-footer::after {{
    display: none;
  }}
}}
{CSS_END}
'''


def replace_marked_block(text: str, block: str) -> str:
    pattern = re.compile(re.escape(CSS_START) + r".*?" + re.escape(CSS_END), re.S)
    if pattern.search(text):
        return pattern.sub(block.strip(), text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block.strip() + "\n"


def assert_content_order(html: str) -> None:
    required = [
        "Franciele Sofiati signature logo",
        ">Brand<",
        "Franciele Sofiati",
        "Advanced Aesthetic Biomedicine",
        "CRBM 6277",
        "Laser and skin care guided by professional evaluation in Londrina, PR.",
        ">Consultation<",
        ">Main Pages<",
        ">Home<",
        ">About<",
        ">Care<",
        ">Laser<",
        ">Skin<",
        ">Results<",
        ">Consultation<",
        ">Contact<",
        ">Brand and Trust<",
        ">Mission<",
        ">Values<",
        ">Testimonials<",
        ">FAQ<",
        ">Journal<",
        ">Blog<",
        ">Legal<",
        ">Legal<",
        ">Privacy<",
        ">Cookies<",
        ">Accessibility<",
        ">Sitemap<",
        ">Contact<",
        "WhatsApp: (43) 9 9104-3536",
        "sofiatimendonca@gmail.com",
        "@fransofiati_biomedica",
        "Londrina, PR",
    ]

    pos = -1
    for token in required:
        next_pos = html.find(token, pos + 1)
        if next_pos == -1:
            raise ValueError(f"Footer content order check failed. Missing or out of order: {token}")
        pos = next_pos


def assert_no_boxes_around_link_columns(css: str) -> None:
    # These should only appear in global reset as transparent/0/none, not recipe styling for groups.
    forbidden_patterns = [
        r"\.footer-link-group\s*\{[^}]*background:\s*(?!transparent\s*!important)",
        r"\.footer-link-group\s*\{[^}]*border:\s*(?!0\s*!important)",
        r"\.footer-link-group\s*\{[^}]*box-shadow:\s*(?!none\s*!important)",
        r"\.footer-link-group\s*\{[^}]*border-radius:\s*(?!0\s*!important)",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, css, re.S):
            raise ValueError("Footer link columns contain boxed styling. Remove background/border/shadow/radius.")


def recipe_signature(recipe: FooterRecipe) -> tuple[str, ...]:
    return (
        recipe.bg,
        recipe.width,
        recipe.columns,
        recipe.pad_top,
        recipe.pad_bottom,
        recipe.column_gap,
        recipe.icon_style,
        recipe.divider_style,
        recipe.hover_style,
        recipe.brand_align,
        recipe.mobile_order,
    )


def assert_unique_recipes() -> None:
    seen: dict[tuple[str, ...], int] = {}
    for number, recipe in FOOTER_RECIPES.items():
        sig = recipe_signature(recipe)
        if sig in seen:
            raise ValueError(f"Footer recipe {number} duplicates recipe {seen[sig]}")
        seen[sig] = number


def git_is_dirty(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def backup_file(path: Path) -> None:
    if path.exists():
        backup = path.with_suffix(path.suffix + ".footer-v3.bak")
        shutil.copy2(path, backup)


def write_text(path: Path, content: str, apply: bool) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == content:
        return False

    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        backup_file(path)
        path.write_text(content, encoding="utf-8")

    return True


def append_audit(root: Path, lines: list[str], apply: bool) -> None:
    audit_path = root / "audit" / "footer-variation-audit.md"
    if apply:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Write changes. Without this, runs dry.")
    parser.add_argument("--force", action="store_true", help="Allow running on a dirty git tree.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    concepts_dir = root / "concepts"

    assert_unique_recipes()

    if git_is_dirty(root) and not args.force:
        print("Git tree has changes. Commit/stash first, or rerun with --force.")
        return

    audit_lines = [
        "# Sofiati Footer Variation Audit",
        "",
        "Rules:",
        "- Same content order in every footer.",
        "- No boxes around link columns.",
        "- 50 named footer recipes.",
        "- Colour, spacing, icons, dividers and hover rhythm vary by concept.",
        "",
    ]

    changed_count = 0

    for concept in concept_dirs(concepts_dir):
        number = concept_number(concept)
        recipe = FOOTER_RECIPES.get(number)

        if not recipe:
            print(f"Skipping {concept.name}: no footer recipe.")
            continue

        code = f"{number:02d}"
        partial_path = concept / "partials" / "footer.html"
        css_path = find_css_file(concept)

        footer_html = render_footer_html(recipe, code)
        assert_content_order(footer_html)

        css_block = render_footer_css(recipe, code)
        assert_no_boxes_around_link_columns(css_block)

        existing_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        new_css = replace_marked_block(existing_css, css_block)

        changed_html = write_text(partial_path, footer_html, args.apply)
        changed_css = write_text(css_path, new_css, args.apply)

        if changed_html or changed_css:
            changed_count += 1

        audit_lines.extend([
            f"## {concept.name}",
            "",
            f"- Recipe: `{recipe.slug}`",
            f"- Background: `{recipe.bg}`",
            f"- Width: `{recipe.width}`",
            f"- Columns: `{recipe.columns}`",
            f"- Padding: `{recipe.pad_top}` / `{recipe.pad_bottom}`",
            f"- Gap: `{recipe.column_gap}`",
            f"- Icon style: `{recipe.icon_style}`",
            f"- Divider style: `{recipe.divider_style}`",
            f"- Hover style: `{recipe.hover_style}`",
            f"- Brand alignment: `{recipe.brand_align}`",
            f"- Mobile order: `{recipe.mobile_order}`",
            "- Link column boxes: `false`",
            "- Content order unchanged: `true`",
            "",
        ])

        print(f"{'Would update' if not args.apply else 'Updated'} {concept.name}")

    append_audit(root, audit_lines, args.apply)

    if args.apply:
        print(f"Done. Updated {changed_count} concepts.")
        print("Audit written to audit/footer-variation-audit.md")
    else:
        print(f"Dry run complete. {changed_count} concepts would change.")
        print("Rerun with --apply to write files.")


if __name__ == "__main__":
    main()