import { useEffect, useRef, useState } from 'react';

import { v4 as uuidv4 } from 'uuid';

import { useWebSocket } from '@/hooks/useWebSocket';
import { useChatStore } from '@/stores/chatStore';

type InputMode = 'text' | 'file' | 'url';

export function InputBar() {
  const [inputText, setInputText] = useState('');
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [error, setError] = useState('');

  const { send, isConnected } = useWebSocket();
  const loading = useChatStore((state) => state.loading);
  const sessionId = useChatStore((state) => state.sessionId);
  const addMessage = useChatStore((state) => state.addMessage);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const textInputRef = useRef<HTMLInputElement>(null);
  const urlInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (inputMode === 'text') {
      textInputRef.current?.focus();
    }
    if (inputMode === 'url') {
      urlInputRef.current?.focus();
    }
  }, [inputMode]);

  async function handleSendText() {
    if (!inputText.trim() || !isConnected || loading || !sessionId) return;

    const content = inputText.trim();
    const userMsg = {
      id: uuidv4(),
      role: 'user' as const,
      content,
      timestamp: new Date(),
    };

    addMessage(userMsg);
    setInputText('');
    setError('');
    useChatStore.getState().setLoading(true);

    try {
      const res = await fetch('/api/v1/chat/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ session_id: sessionId, query: content }),
      });

      if (!res.ok) {
        const payload = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(payload.detail ?? 'Failed to send message');
      }
    } catch (err) {
      setError(String(err));
      useChatStore.getState().setLoading(false);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !sessionId) return;

    setSelectedFile(file);

    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
    ];

    if (!validTypes.includes(file.type)) {
      setError('Invalid file type. Use PDF, DOCX, or TXT.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Max 10MB.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`/api/v1/upload-document?session_id=${sessionId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: formData,
      });

      if (response.ok) {
        setError('');
        setSelectedFile(null);
        setInputMode('text');

        const userMsg = {
          id: uuidv4(),
          role: 'user' as const,
          content: `Uploaded document: ${file.name}`,
          timestamp: new Date(),
        };
        addMessage(userMsg);

        send(JSON.stringify({ type: 'document', filename: file.name }));
      } else {
        setError('Upload failed');
      }
    } catch (err) {
      setError('Upload error: ' + String(err));
    }
  }

  async function handleUrlSubmit() {
    if (!urlInput.trim() || !isConnected || loading || !sessionId) return;

    try {
      new URL(urlInput);
    } catch {
      setError('Invalid URL');
      return;
    }

    try {
      const response = await fetch(`/api/v1/ingest-url?session_id=${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ url: urlInput }),
      });

      if (response.ok) {
        setError('');
        setUrlInput('');
        setInputMode('text');

        const userMsg = {
          id: uuidv4(),
          role: 'user' as const,
          content: `Added URL: ${urlInput}`,
          timestamp: new Date(),
        };
        addMessage(userMsg);

        send(JSON.stringify({ type: 'url', url: urlInput }));
      } else {
        setError('URL ingestion failed');
      }
    } catch (err) {
      setError('Error: ' + String(err));
    }
  }

  function handleTextKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault();
      void handleSendText();
    }
  }

  function handleUrlKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault();
      void handleUrlSubmit();
    }
  }

  return (
    <div className="p-4 bg-white border-t border-gray-200">
      <div className="max-w-3xl mx-auto">
        {error && (
          <div className="p-3 mb-4 text-sm text-red-700 border border-red-200 rounded bg-red-50">{error}</div>
        )}

        <div className="flex flex-col gap-3 md:flex-row">
          <div className="flex p-1 bg-gray-100 rounded-lg">
            <button
              onClick={() => setInputMode('text')}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                inputMode === 'text' ? 'bg-white text-blue-600 shadow' : 'text-gray-600 hover:text-gray-900'
              }`}
              type="button"
            >
              💬 Text
            </button>
            <button
              onClick={() => setInputMode('file')}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                inputMode === 'file' ? 'bg-white text-blue-600 shadow' : 'text-gray-600 hover:text-gray-900'
              }`}
              type="button"
            >
              📄 File
            </button>
            <button
              onClick={() => setInputMode('url')}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                inputMode === 'url' ? 'bg-white text-blue-600 shadow' : 'text-gray-600 hover:text-gray-900'
              }`}
              type="button"
            >
              🔗 URL
            </button>
          </div>

          <div className="flex-1">
            {inputMode === 'text' && (
              <div className="flex gap-2">
                <input
                  ref={textInputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleTextKeyDown}
                  placeholder="Ask about market trends, competitors, pricing..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading || !isConnected || !sessionId}
                />
              </div>
            )}

            {inputMode === 'file' && (
              <div className="flex gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-1 py-2 text-center transition border-2 border-gray-300 border-dashed rounded-lg hover:bg-gray-50"
                  type="button"
                  disabled={loading || !isConnected || !sessionId}
                >
                  {selectedFile ? `Selected: ${selectedFile.name}` : 'Click to upload PDF, DOCX, or TXT'}
                </button>
              </div>
            )}

            {inputMode === 'url' && (
              <div className="flex gap-2">
                <input
                  ref={urlInputRef}
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  onKeyDown={handleUrlKeyDown}
                  placeholder="https://example.com"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading || !isConnected || !sessionId}
                />
              </div>
            )}
          </div>

          <button
            onClick={() => {
              if (inputMode === 'text') {
                void handleSendText();
              } else if (inputMode === 'file') {
                fileInputRef.current?.click();
              } else if (inputMode === 'url') {
                void handleUrlSubmit();
              }
            }}
            disabled={loading || !isConnected || !sessionId}
            className="px-6 py-2 font-medium text-white transition bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            type="button"
          >
            {loading ? '⏳' : '→'}
          </button>
        </div>

        <div className="mt-2 text-xs text-gray-500">{!isConnected ? '🔴 Disconnected' : '🟢 Connected'}</div>
      </div>
    </div>
  );
}
