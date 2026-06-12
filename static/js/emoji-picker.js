const EMOJI_CATS = [
  {
    label: 'Common',
    emojis: ['🏷️','⭐','❤️','🔥','✅','⚠️','📌','🎯','💬','🔔','🗂️','📎','🔗','💡','🚀','🌟'],
  },
  {
    label: 'Work',
    emojis: ['💼','📋','📝','📊','📈','📉','🗓️','⏰','🔑','📧','🖥️','🖨️','📠','🗃️','🏢','👔'],
  },
  {
    label: 'Study',
    emojis: ['📚','🎓','🔬','📖','✏️','🧪','🧠','🔭','📐','📏','🗒️','📓','📔','📕','📗','📘'],
  },
  {
    label: 'Life',
    emojis: ['🏠','🎮','🎵','🎨','🏃','😊','💪','🌿','🍎','☕','🌍','✈️','🎉','🤝','👨‍👩‍👧','❓'],
  },
  {
    label: 'Status',
    emojis: ['🟢','🟡','🔴','🔵','🟣','⚪','⚫','🟤','🔶','🔷','🔸','🔹','▶️','⏸️','⏹️','🔄'],
  },
];

/**
 * EmojiPicker — attaches to a container element.
 *
 * Usage:
 *   const picker = new EmojiPicker(containerEl, { onChange: emoji => ... });
 *   picker.getValue()  → current emoji string or ''
 *   picker.setValue(emoji)
 *   picker.clear()
 */
class EmojiPicker {
  constructor(container, { onChange } = {}) {
    this._value    = '';
    this._onChange = onChange || (() => {});
    this._build(container);
    this._activateCat(0);

    // Close on outside click
    document.addEventListener('click', e => {
      if (!container.contains(e.target)) this._close();
    });
  }

  _build(container) {
    container.style.position = 'relative';

    // Trigger button
    this._trigger = document.createElement('button');
    this._trigger.type = 'button';
    this._trigger.className = 'ep-trigger';
    this._trigger.innerHTML = `
      <span class="ep-preview"></span>
      <span class="ep-placeholder">Pick an icon…</span>
    `;
    this._trigger.addEventListener('click', e => { e.stopPropagation(); this._toggle(); });

    // Popover
    this._popover = document.createElement('div');
    this._popover.className = 'ep-popover';

    // Category tabs
    const cats = document.createElement('div');
    cats.className = 'ep-cats';
    this._catBtns = EMOJI_CATS.map((cat, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ep-cat';
      btn.textContent = cat.label;
      btn.addEventListener('click', () => this._activateCat(i));
      cats.appendChild(btn);
      return btn;
    });

    // Emoji grid
    this._grid = document.createElement('div');
    this._grid.className = 'ep-grid';

    // Clear button
    const clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'ep-clear';
    clear.textContent = 'Clear';
    clear.addEventListener('click', () => { this.clear(); this._close(); });

    this._popover.append(cats, this._grid, clear);
    container.append(this._trigger, this._popover);
  }

  _activateCat(index) {
    this._catBtns.forEach((b, i) => b.classList.toggle('is-active', i === index));
    const emojis = EMOJI_CATS[index].emojis;
    this._grid.innerHTML = '';
    emojis.forEach(em => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ep-emoji';
      btn.textContent = em;
      btn.title = em;
      btn.addEventListener('click', () => { this._select(em); this._close(); });
      this._grid.appendChild(btn);
    });
  }

  _select(emoji) {
    this._value = emoji;
    this._trigger.querySelector('.ep-preview').textContent = emoji;
    this._trigger.querySelector('.ep-placeholder').style.display = 'none';
    this._onChange(emoji);
  }

  _toggle() { this._popover.classList.toggle('is-open'); }
  _close()  { this._popover.classList.remove('is-open'); }

  getValue()      { return this._value; }
  setValue(emoji) { emoji ? this._select(emoji) : this.clear(); }
  clear() {
    this._value = '';
    this._trigger.querySelector('.ep-preview').textContent = '';
    this._trigger.querySelector('.ep-placeholder').style.display = '';
    this._onChange('');
  }
}
