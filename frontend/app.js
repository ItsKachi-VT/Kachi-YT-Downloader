const els = {
  urlInput: document.getElementById('urlInput'),
  formatSelect: document.getElementById('formatSelect'),
  resolutionSelect: document.getElementById('resolutionSelect'),
  outputPath: document.getElementById('outputPath'),
  browseBtn: document.getElementById('browseBtn'),
  downloadBtn: document.getElementById('downloadBtn'),
  progressFill: document.getElementById('progressFill'),
  stateTitle: document.getElementById('stateTitle'),
  progressLabel: document.getElementById('progressLabel'),
  statusMessage: document.getElementById('statusMessage'),
  statusPill: document.getElementById('statusPill'),
  historyList: document.getElementById('historyList'),
  downloadView: document.getElementById('downloadView'),
  historyView: document.getElementById('historyView'),
  menuItems: document.querySelectorAll('.menu-item')
};

const callPywebviewApi = async (method, ...args) => {
  const api = window.pywebview && window.pywebview.api ? window.pywebview.api : null;
  if (!api || typeof api[method] !== 'function') {
    throw new Error(`La API de Python no está disponible: ${method}`);
  }
  return api[method](...args);
};

const setStatus = (label, progress, text, tone = 'ready') => {
  els.stateTitle.textContent = label;
  els.progressLabel.textContent = `${Math.max(0, Math.min(100, progress))}%`;
  els.progressFill.style.width = `${Math.max(0, Math.min(100, progress))}%`;
  els.statusMessage.textContent = text;

  const map = {
    ready: { bg: 'rgba(57, 217, 138, 0.12)', border: 'rgba(57, 217, 138, 0.28)', color: '#39d98a' },
    busy: { bg: 'rgba(124, 156, 255, 0.12)', border: 'rgba(124, 156, 255, 0.28)', color: '#7c9cff' },
    error: { bg: 'rgba(255, 93, 115, 0.12)', border: 'rgba(255, 93, 115, 0.28)', color: '#ff5d73' }
  };

  const styles = map[tone] || map.ready;
  els.statusPill.style.background = styles.bg;
  els.statusPill.style.borderColor = styles.border;
  els.statusPill.style.color = styles.color;
};

const setDefaultFolder = async () => {
  try {
    const result = await callPywebviewApi('request_downloads_access');
    if (result) {
      els.outputPath.value = result;
    }
  } catch (error) {
    console.error('No se pudo obtener la carpeta de descargas', error);
    els.outputPath.value = '';
  }
};

const renderHistory = async () => {
  try {
    const history = await callPywebviewApi('get_history');
    if (!Array.isArray(history) || history.length === 0) {
      els.historyList.innerHTML = '<div class="history-empty">No hay descargas aún.</div>';
      return;
    }

    els.historyList.innerHTML = history.map((item) => `
      <div class="history-item">
        <div class="history-main">
          <strong>${(item.title || 'Archivo').slice(0, 50)}</strong>
          <span>${item.fecha}</span>
        </div>
        <div class="history-meta">
          <span>${item.tipo} · ${item.formato}</span>
          <span>${item.resolucion}</span>
        </div>
        <div class="history-path">${item.ruta}</div>
      </div>
    `).join('');
  } catch (error) {
    els.historyList.innerHTML = '<div class="history-empty">No se pudo cargar el historial.</div>';
  }
};

const setView = (target) => {
  const isDownload = target === 'download';
  els.downloadView.classList.toggle('hidden', !isDownload);
  els.historyView.classList.toggle('hidden', isDownload);
  els.menuItems.forEach((item) => {
    const active = item.dataset.view === target;
    item.classList.toggle('active', active);
  });

  if (target === 'history') {
    renderHistory();
  }
};

els.menuItems.forEach((item) => {
  item.addEventListener('click', () => setView(item.dataset.view));
});

setDefaultFolder();

const updateResolutionState = () => {
  const isAudio = els.formatSelect.value === 'audio_mp3';
  els.resolutionSelect.disabled = isAudio;
  els.resolutionSelect.style.opacity = isAudio ? '0.55' : '1';
};

els.formatSelect.addEventListener('change', updateResolutionState);
updateResolutionState();

els.browseBtn.addEventListener('click', async () => {
  try {
    const result = await callPywebviewApi('select_folder');
    if (result) {
      els.outputPath.value = result;
    }
  } catch (error) {
    console.error(error);
    setStatus('Carpeta no disponible', 0, 'No se pudo abrir el selector de carpeta.', 'error');
  }
});

els.downloadBtn.addEventListener('click', async () => {
  const url = els.urlInput.value.trim();
  const outputFormat = els.formatSelect.value;
  const resolution = els.resolutionSelect.value;
  const folder = els.outputPath.value.trim();

  if (!url) {
    setStatus('URL requerida', 0, 'Debes ingresar un enlace válido.', 'error');
    return;
  }

  els.downloadBtn.disabled = true;
  setStatus('Preparando', 5, 'Validando enlace y preparando la descarga...', 'busy');

  try {
    const response = await callPywebviewApi('download', url, outputFormat, resolution, folder);
    if (response && response.ok) {
      setStatus('Descarga completada', 100, response.message || 'Listo.', 'ready');
    } else {
      setStatus('Error', 0, response?.message || 'No se pudo completar la descarga.', 'error');
    }
  } catch (error) {
    const message = error?.message || 'Error inesperado.';
    setStatus('Error', 0, message, 'error');
  } finally {
    els.downloadBtn.disabled = false;
  }
});

setInterval(async () => {
  try {
    const state = await callPywebviewApi('status');
    if (!state) return;

    const status = state.status || 'idle';
    const progress = Number(state.progress || 0);
    const detail = state.detail || 'Listo para descargar.';
    const error = state.error || '';

    if (status === 'downloading') {
      setStatus('Descargando', progress, detail, 'busy');
    } else if (status === 'preparing') {
      setStatus('Preparando', progress, detail, 'busy');
    } else if (status === 'done') {
      setStatus('Completado', 100, detail, 'ready');
    } else if (status === 'error') {
      setStatus('Error', 0, error || detail, 'error');
    } else {
      setStatus('Listo', 0, detail, 'ready');
    }
  } catch (error) {
    console.error('status polling error', error);
  }
}, 700);
