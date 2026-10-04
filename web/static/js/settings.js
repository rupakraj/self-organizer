// ── Tab switching ─────────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('is-active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('is-active'));
    btn.classList.add('is-active');
    document.getElementById(`tab-${target}`).classList.add('is-active');
  });
});


// ── Shared CRUD factory ───────────────────────────────────────────────────────
// Creates a self-contained CRUD controller for any tag-like resource.
// Options: { apiBase, bodyId, modalId, titleId, errorId, nameId, slugId, colorId, iconPickerId }

function makeCrudController({ apiBase, bodyId, modalId, titleId, errorId, nameId, slugId, colorId, iconPickerId }) {
  let _editId = null;

  const modal      = document.getElementById(modalId);
  const titleEl    = document.getElementById(titleId);
  const errBox     = document.getElementById(errorId);
  const fName      = document.getElementById(nameId);
  const fSlug      = document.getElementById(slugId);
  const fColor     = document.getElementById(colorId);
  const iconPicker = new EmojiPicker(document.getElementById(iconPickerId));

  let slugEdited = false;
  fSlug.addEventListener('input', () => { slugEdited = true; });
  fName.addEventListener('input', () => {
    if (!slugEdited) {
      fSlug.value = fName.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    }
  });

  function _clearForm() {
    fName.value  = '';
    fSlug.value  = '';
    fColor.value = '#6366f1';
    slugEdited   = false;
    iconPicker.clear();
    errBox.textContent = '';
    errBox.classList.add('hidden');
  }

  function openAdd() {
    _editId = null;
    _clearForm();
    titleEl.textContent = `Add ${_label()}`;
    modal.classList.add('is-open');
    fName.focus();
  }

  function openEdit(item) {
    _editId = item.id;
    _clearForm();
    fName.value  = item.name;
    fSlug.value  = item.slug;
    fColor.value = item.color;
    slugEdited   = true;
    iconPicker.setValue(item.icon || '');
    titleEl.textContent = `Edit ${_label()}`;
    modal.classList.add('is-open');
    fName.focus();
  }

  function closeModal() {
    modal.classList.remove('is-open');
  }

  async function submit() {
    const body = {
      name:  fName.value.trim(),
      slug:  fSlug.value.trim(),
      icon:  iconPicker.getValue(),
      color: fColor.value,
    };
    const url    = _editId ? `${apiBase}/${_editId}` : apiBase;
    const method = _editId ? 'PUT' : 'POST';

    const res  = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) {
      errBox.textContent = data.error || 'Something went wrong.';
      errBox.classList.remove('hidden');
      return;
    }
    closeModal();
    load();
  }

  async function _toggleActive(item) {
    const url    = item.is_active ? `${apiBase}/${item.id}` : `${apiBase}/${item.id}/restore`;
    const method = item.is_active ? 'DELETE' : 'POST';
    await fetch(url, { method });
    load();
  }

  function _label() {
    // Derive a human label from the API base path, e.g. '/api/tags' → 'Tag'
    const seg = apiBase.split('/').pop();
    return seg.charAt(0).toUpperCase() + seg.slice(1, -1); // strip trailing 's'
  }

  function _renderRow(item) {
    const tr = document.createElement('tr');
    if (!item.is_active) tr.classList.add('is-inactive');

    const nameCell    = item.is_active ? item.name : `<span class="line-through">${item.name}</span>`;
    const toggleLabel = item.is_active ? 'Deactivate' : 'Restore';
    const toggleClass = item.is_active
      ? 'text-red-400 hover:text-red-600'
      : 'text-green-500 hover:text-green-700';

    tr.innerHTML = `
      <td>
        <span class="inline-block w-5 h-5 rounded-full border border-gray-200"
              style="background:${item.color}"></span>
      </td>
      <td>${item.icon ? `<span class="mr-1">${item.icon}</span>` : ''}${nameCell}</td>
      <td class="font-mono text-gray-400 text-xs">${item.slug}</td>
      <td class="text-lg">${item.icon || '—'}</td>
      <td>
        <span class="badge ${item.is_active ? 'badge--active' : 'badge--todo'}">
          ${item.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td class="flex items-center gap-3">
        ${item.is_active ? `<button class="text-indigo-400 hover:text-indigo-600 text-xs font-medium" data-edit>Edit</button>` : ''}
        <button class="${toggleClass} text-xs font-medium" data-toggle>${toggleLabel}</button>
      </td>
    `;

    if (item.is_active) {
      tr.querySelector('[data-edit]').addEventListener('click', () => openEdit(item));
    }
    tr.querySelector('[data-toggle]').addEventListener('click', () => _toggleActive(item));
    return tr;
  }

  async function load() {
    const res   = await fetch(apiBase);
    const items = await res.json();
    const body  = document.getElementById(bodyId);
    body.innerHTML = '';

    if (!items.length) {
      body.innerHTML = `<tr><td colspan="6" class="text-center text-gray-400 py-6">No ${apiBase.split('/').pop()} yet.</td></tr>`;
      return;
    }
    items.forEach(item => body.appendChild(_renderRow(item)));
  }

  load();

  return { openAdd, openEdit, closeModal, submit };
}


// ── Controllers ───────────────────────────────────────────────────────────────

const Tags = makeCrudController({
  apiBase:      '/api/tags',
  bodyId:       'tags-body',
  modalId:      'tag-modal',
  titleId:      'tag-modal-title',
  errorId:      'tag-modal-error',
  nameId:       't-name',
  slugId:       't-slug',
  colorId:      't-color',
  iconPickerId: 't-icon-picker',
});

const Categories = makeCrudController({
  apiBase:      '/api/categories',
  bodyId:       'categories-body',
  modalId:      'cat-modal',
  titleId:      'cat-modal-title',
  errorId:      'cat-modal-error',
  nameId:       'c-name',
  slugId:       'c-slug',
  colorId:      'c-color',
  iconPickerId: 'c-icon-picker',
});
