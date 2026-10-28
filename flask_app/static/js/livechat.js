(function () {
  'use strict';

  // ===== ELEMENTS =====
  const messagesDiv  = document.getElementById('chat-messages');
  const inputEl      = document.getElementById('user-input');
  const sendBtn      = document.getElementById('send-btn');
  const resetBtn     = document.getElementById('btn-reset');
  const charCounter  = document.getElementById('char-counter');
  const quickReplies = document.getElementById('quick-replies');

  // ===== UTILITY =====
  function getCurrentTime() {
    return new Date().toLocaleTimeString('id-ID', {
      hour: '2-digit', minute: '2-digit'
    });
  }

  function scrollToBottom() {
    messagesDiv.scrollTo({
      top: messagesDiv.scrollHeight,
      behavior: 'smooth'
    });
  }

  // ===== APPEND MESSAGE =====
  function appendMessage(text, isUser, source) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${isUser ? 'user' : 'bot'}`;

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${isUser ? 'user-avatar-sm' : 'bot-avatar-sm'}`;
    avatar.textContent = isUser ? '👤' : '🤗';

    // Content
    const content = document.createElement('div');
    content.className = 'message-content';

    // Bubble
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'}`;
    bubble.textContent = text;

    // Meta
    const meta = document.createElement('div');
    meta.className = 'message-meta';

    if (isUser) {
      meta.innerHTML = `
        <span>${getCurrentTime()}</span>
        <span>Anda</span>
      `;
    } else {
      const badgeClass = source === 'gemini' ? 'gemini' : '';
      const badgeLabel = source === 'gemini'  ? 'AI Assistant' :
                         source === 'seq2seq' ? 'AI Assistant'   : 'AI Assistant';
      meta.innerHTML = `
        <span>CareBot</span>
        ${source ? `<span class="source-badge ${badgeClass}">${badgeLabel}</span>` : ''}
        <span>${getCurrentTime()}</span>
      `;
    }

    content.appendChild(bubble);
    content.appendChild(meta);
    wrapper.appendChild(avatar);
    wrapper.appendChild(content);
    messagesDiv.appendChild(wrapper);
    scrollToBottom();
  }

  // ===== TYPING INDICATOR =====
  function showTyping() {
    const wrapper = document.createElement('div');
    wrapper.className = 'typing-wrapper';
    wrapper.id = 'typing-indicator';
    wrapper.innerHTML = `
      <div class="message-avatar bot-avatar-sm">🤗</div>
      <div class="typing-bubble">
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    messagesDiv.appendChild(wrapper);
    scrollToBottom();
  }

  function hideTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  // ===== SEND MESSAGE =====
  async function sendMessage(text) {
    const message = text || inputEl.value.trim();
    if (!message) return;

    // Sembunyikan quick replies
    if (quickReplies) {
      quickReplies.style.display = 'none';
    }

    // Tampilkan pesan user
    appendMessage(message, true);

    // Reset input
    if (!text) {
      inputEl.value = '';
      inputEl.style.height = 'auto';
      charCounter.textContent = '0/500';
      charCounter.style.color = '#adb5bd';
    }

    // Disable send button
    sendBtn.disabled = true;
    showTyping();

    try {
      const res = await fetch('/chat', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ message })
      });

      const data = await res.json();
      hideTyping();

      if (!res.ok || data.error) {
        appendMessage(
          data.error || 'Maaf, terjadi kesalahan. Silakan coba lagi.',
          false
        );
      } else {
        appendMessage(data.response, false, data.source);
      }

    } catch (err) {
      hideTyping();
      appendMessage(
        'Koneksi bermasalah. Pastikan server berjalan dan coba lagi.',
        false
      );
      console.error('Fetch error:', err);
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  // ===== QUICK REPLY =====
  window.sendQuickReply = function (text) {
    sendMessage(text);
  };

  // ===== RESET CHAT =====
  async function resetChat() {
    try {
      await fetch('/reset', { method: 'POST' });
    } catch (err) {
      console.error('Reset error:', err);
    }

    // Hapus semua pesan
    const messages = messagesDiv.querySelectorAll('.message-wrapper');
    messages.forEach(m => m.remove());

    // Tampilkan kembali quick replies
    if (quickReplies) {
      quickReplies.style.display = 'flex';
    }

    // Pesan reset
    appendMessage(
      'Percakapan baru dimulai. Ada yang ingin Anda ceritakan? 😊',
      false
    );

    inputEl.focus();
  }

  // ===== EVENT LISTENERS =====
  sendBtn.addEventListener('click', () => sendMessage());

  inputEl.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  inputEl.addEventListener('input', function () {
    // Auto resize textarea
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';

    // Update char counter
    const len = this.value.length;
    charCounter.textContent = `${len}/500`;
    charCounter.style.color = len > 450 ? '#dc3545' :
                              len > 400 ? '#fd7e14' : '#adb5bd';
  });

  if (resetBtn) {
    resetBtn.addEventListener('click', resetChat);
  }

  // ===== INIT =====
  inputEl.focus();

})();