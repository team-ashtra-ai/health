function makeMarker(sectionHead) {
  const number = sectionHead.querySelector(':scope > .sf-chapter-number');
  const eyebrow = sectionHead.querySelector(':scope > .sf-eyebrow');

  if (!number || !eyebrow || sectionHead.querySelector(':scope > .sf-editorial-marker')) return;

  const value = Number.parseInt(number.textContent, 10);
  if (Number.isFinite(value)) number.textContent = String(value).padStart(2, '0');

  const marker = document.createElement('div');
  marker.className = 'sf-editorial-marker';
  marker.setAttribute('aria-hidden', 'true');
  sectionHead.insertBefore(marker, number);
  marker.append(number, eyebrow);
}

function markMediaSide(layout) {
  const media = layout.querySelector(':scope > .sf-editorial-media');
  const copy = layout.querySelector(':scope > .sf-section-inner');
  if (!media || !copy) return;

  const mediaColumn = Number.parseInt(getComputedStyle(media).gridColumnStart, 10);
  const copyColumn = Number.parseInt(getComputedStyle(copy).gridColumnStart, 10);
  layout.classList.toggle('sf-editorial-media-layout--media-left', Number.isFinite(mediaColumn) && Number.isFinite(copyColumn) && mediaColumn < copyColumn);
}

export function initEditorialMarkers() {
  document.querySelectorAll('.sf-section-head, .sf-editorial-kicker, .sf-form-section-intro').forEach(makeMarker);

  const updateMediaSides = () => document.querySelectorAll('.sf-editorial-media-layout').forEach(markMediaSide);
  updateMediaSides();
  window.addEventListener('resize', updateMediaSides, { passive: true });
}
