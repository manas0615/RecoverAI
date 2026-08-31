import re

with open('frontend/src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

old_css = """/* Transparent page scrollbar (Screen 01 Micro-fix) */
html, body, main {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

html::-webkit-scrollbar,
body::-webkit-scrollbar,
main::-webkit-scrollbar {
  width: 0px;
  height: 0px;
  background: transparent;
  display: none;
}

html::-webkit-scrollbar-track,
body::-webkit-scrollbar-track,
main::-webkit-scrollbar-track {
  background: transparent;
}

html::-webkit-scrollbar-thumb,
body::-webkit-scrollbar-thumb,
main::-webkit-scrollbar-thumb {
  background: transparent;
}"""

new_css = """/* Subtle page scrollbar (Screen 01 Final Micro-fix) */
html, body, main {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

html::-webkit-scrollbar,
body::-webkit-scrollbar,
main::-webkit-scrollbar {
  width: 6px;
  height: 6px;
  background: transparent;
}

html::-webkit-scrollbar-track,
body::-webkit-scrollbar-track,
main::-webkit-scrollbar-track {
  background: transparent;
}

html::-webkit-scrollbar-thumb,
body::-webkit-scrollbar-thumb,
main::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

html::-webkit-scrollbar-thumb:hover,
body::-webkit-scrollbar-thumb:hover,
main::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}"""

if old_css in css:
    css = css.replace(old_css, new_css)
else:
    print("Warning: old CSS not found, appending directly")
    css += "\n" + new_css

with open('frontend/src/index.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated CSS")
