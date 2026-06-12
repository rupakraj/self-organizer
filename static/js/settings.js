// Tab switching

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('is-active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('is-active'));
    btn.classList.add('is-active');
    document.getElementById(`tab-${target}`).classList.add('is-active');
  });
});


// Tags

const Tags = (() => {
  let _editId = null;

  const modal  = document.getElementById('tag-modal');
  const title  = document.getElementById('modal-title');
  const errBox = document.getElementById('modal-error');
  const fName  = document.getElementById('f-name');
  const fSlug  = document.getElementById('f-slug');
  const fColor = document.getElementById('f-color');

  // Emoji picker instance
  const iconPicker = new EmojiPicker(document.getElementById('f-icon-picker'));

  // Auto-generate slug from name unless user has manually edited it
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
    title.textContent = 'Add Tag';
    modal.classList.add('is-open');
    fName.focus();
  }

  function openEdit(tag) {
    _editId = tag.id;
    _clearForm();
    fName.value  = tag.name;
    fSlug.value  = tag.slug;
    fColor.value = tag.color;
    slugEdited   = true;
    iconPicker.setValue(tag.icon || '');
    title.textContent = 'Edit Tag';
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

    const url    = _editId ? `/api/tags/${_editId}` : '/api/tags';
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
    loadTags();
  }

  async function toggleActive(tag) {
    const url    = tag.is_active ? `/api/tags/${tag.id}` : `/api/tags/${tag.id}/restore`;
    const method = tag.is_active ? 'DELETE' : 'POST';
    await fetch(url, { method });
    loadTags();
  }

  function _renderRow(tag) {
    const tr = document.createElement('tr');
    if (!tag.is_active) tr.classList.add('is-inactive');

    const nameCell = tag.is_active ? tag.name : `<span class="line-through">${tag.name}</span>`;
    const toggleLabel = tag.is_active ? 'Deactivate' : 'Restore';
    const toggleClass = tag.is_active
      ? 'text-red-400 hover:text-red-600'
      : 'text-green-500 hover:text-green-700';

    tr.innerHTML = `
      <td>
        <span class="inline-block w-5 h-5 rounded-full border border-gray-200"
              style="background:${tag.color}"></span>
      </td>
      <td>${tag.icon ? `<span class="mr-1">${tag.icon}</span>` : ''}${nameCell}</td>
      <td class="font-mono text-gray-400 text-xs">${tag.slug}</td>
      <td class="text-lg">${tag.icon || '—'}</td>
      <td>
        <span class="badge ${tag.is_active ? 'badge--active' : 'badge--todo'}">
          ${tag.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td class="flex items-center gap-3">
        ${tag.is_active ? `<button class="text-indigo-400 hover:text-indigo-600 text-xs font-medium" data-edit>Edit</button>` : ''}
        <button class="${toggleClass} text-xs font-medium" data-toggle>${toggleLabel}</button>
      </td>
    `;

    if (tag.is_active) {
      tr.querySelector('[data-edit]').addEventListener('click', () => openEdit(tag));
    }
    tr.querySelector('[data-toggle]').addEventListener('click', () => toggleActive(tag));
    return tr;
  }

  async function loadTags() {
    const res  = await fetch('/api/tags');
    const tags = await res.json();
    const body = document.getElementById('tags-body');
    body.innerHTML = '';

    if (!tags.length) {
      body.innerHTML = '<tr><td colspan="6" class="text-center text-gray-400 py-6">No tags yet.</td></tr>';
      return;
    }
    tags.forEach(tag => body.appendChild(_renderRow(tag)));
  }

  loadTags();

  return { openAdd, openEdit, closeModal, submit };
})();
