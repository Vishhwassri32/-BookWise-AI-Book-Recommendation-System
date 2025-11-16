s// Autocomplete suggestions (AJAX)
const input = document.getElementById('search-input');
const suggestionsBox = document.getElementById('suggestions');

if (input) {
  let timer = null;
  input.addEventListener('input', function() {
    clearTimeout(timer);
    const q = this.value.trim();
    if (q.length < 1) {
      suggestionsBox.style.display = 'none';
      return;
    }
    timer = setTimeout(() => {
      fetch('/_suggest?q=' + encodeURIComponent(q))
        .then(r => r.json())
        .then(list => {
          suggestionsBox.innerHTML = '';
          if (list.length === 0) {
            suggestionsBox.style.display = 'none';
            return;
          }
          list.forEach(item => {
            const div = document.createElement('div');
            div.className = 'item';
            div.textContent = item;
            div.onclick = () => {
              input.value = item;
              suggestionsBox.style.display = 'none';
            };
            suggestionsBox.appendChild(div);
          });
          suggestionsBox.style.display = 'block';
        }).catch(err => {
          suggestionsBox.style.display = 'none';
        });
    }, 250);
  });

  // Hide suggestions when clicking outside
  document.addEventListener('click', function(e) {
    if (!suggestionsBox.contains(e.target) && e.target !== input) {
      suggestionsBox.style.display = 'none';
    }
  });
}

// Voice search (Web Speech API)
const voiceBtn = document.getElementById('voice-btn');
if (voiceBtn && 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const rec = new SpeechRecognition();
  rec.lang = 'en-US';
  rec.interimResults = false;
  rec.maxAlternatives = 1;

  voiceBtn.addEventListener('click', () => {
    rec.start();
    voiceBtn.textContent = '🎤...';
    voiceBtn.disabled = true;
  });

  rec.onresult = (e) => {
    const text = e.results[0][0].transcript;
    const input = document.getElementById('search-input');
    if (input) input.value = text;
    voiceBtn.textContent = '🎤';
    voiceBtn.disabled = false;
    // Optionally submit form automatically:
    // document.querySelector('.search-form').submit();
  };

  rec.onerror = () => {
    voiceBtn.textContent = '🎤';
    voiceBtn.disabled = false;
  };
} else {
  // hide voice button if not supported
  const vb = document.getElementById('voice-btn');
  if (vb) vb.style.display = 'none';
}
