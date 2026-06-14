import { useEffect, useRef, useState } from 'react'
import {
  AudioLines,
  Bot,
  ChevronDown,
  Mic,
  Paperclip,
  Plus,
  Send,
  Sparkles,
  User,
  X,
} from 'lucide-react'
import { runVoiceChat, streamChat, transcribeAudio, type ChatMessage } from '../api/client'
import { useAuth } from '../auth/useAuth'

type ListeningMode = 'dictation' | 'conversation' | null
type VoicePhase = 'idle' | 'listening' | 'processing' | 'speaking'
type ResponseMode = 'instant' | 'deep'
type TextAttachment = { name: string; content: string }

export default function Chat() {
  const { token } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Hello! I\'m your WealthMesh advisor. How can I help you today?' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listeningMode, setListeningMode] = useState<ListeningMode>(null)
  const [voicePhase, setVoicePhase] = useState<VoicePhase>('idle')
  const [voiceSessionActive, setVoiceSessionActive] = useState(false)
  const [responseMode, setResponseMode] = useState<ResponseMode>('instant')
  const [attachment, setAttachment] = useState<TextAttachment | null>(null)
  const [voiceNotice, setVoiceNotice] = useState('')
  const [convId] = useState(() => crypto.randomUUID())
  const bottomRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const voiceSessionRef = useRef(false)
  const animationRef = useRef<number | null>(null)
  const maxRecordingRef = useRef<number | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => () => {
    voiceSessionRef.current = false
    recorderRef.current?.stop()
    streamRef.current?.getTracks().forEach(track => track.stop())
    if (animationRef.current) cancelAnimationFrame(animationRef.current)
    if (maxRecordingRef.current) window.clearTimeout(maxRecordingRef.current)
    window.speechSynthesis?.cancel()
  }, [])

  async function send(message = input, speakReply = false) {
    const cleanMessage = message.trim()
    if (!cleanMessage || loading) return

    const attachmentLabel = attachment ? `\n\nAttached: ${attachment.name}` : ''
    const context = attachment ? `\n\nAttached context (${attachment.name}):\n${attachment.content}` : ''
    const depthInstruction = responseMode === 'deep'
      ? '\n\nPlease provide a thorough analysis with the key assumptions and risks.'
      : ''
    const requestMessage = `${cleanMessage}${context}${depthInstruction}`

    setInput('')
    setAttachment(null)
    setVoiceNotice('')
    setMessages(prev => [
      ...prev,
      { role: 'user', content: `${cleanMessage}${attachmentLabel}` },
      { role: 'assistant', content: '' },
    ])
    setLoading(true)

    let response = ''
    try {
      for await (const tokenChunk of streamChat(requestMessage, convId, token)) {
        response += tokenChunk
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', content: response }
          return updated
        })
      }
      if (speakReply && response.trim()) speak(response)
    } catch {
      const fallback = 'I could not reach the advisory mesh. Please try again.'
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: fallback }
        return updated
      })
      if (speakReply) speak(fallback)
    } finally {
      setLoading(false)
    }
  }

  async function startRecording(mode: Exclude<ListeningMode, null>) {
    setVoiceNotice('')
    if (!navigator.mediaDevices?.getUserMedia || !('MediaRecorder' in window)) {
      setVoiceNotice('Audio recording is not supported in this browser.')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      })
      const preferredType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4']
        .find(type => MediaRecorder.isTypeSupported(type))
      const recorder = new MediaRecorder(stream, preferredType ? { mimeType: preferredType } : undefined)

      chunksRef.current = []
      streamRef.current = stream
      recorderRef.current = recorder
      recorder.ondataavailable = event => {
        if (event.data.size) chunksRef.current.push(event.data)
      }
      recorder.onstop = () => {
        cleanupRecording()
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        if (blob.size < 800) {
          setListeningMode(null)
          setVoicePhase('idle')
          setVoiceNotice('No audio was captured. Check the selected microphone and try again.')
          return
        }
        if (mode === 'dictation') void finishDictation(blob)
        else void finishVoiceTurn(blob)
      }

      recorder.start(250)
      setListeningMode(mode)
      setVoicePhase('listening')
      if (mode === 'conversation') watchForSilence(stream)
      maxRecordingRef.current = window.setTimeout(() => stopRecording(true), mode === 'conversation' ? 20_000 : 60_000)
    } catch (error) {
      const name = error instanceof DOMException ? error.name : ''
      setVoiceNotice(
        name === 'NotAllowedError'
          ? 'Microphone access is blocked. Allow microphone access for localhost, then try again.'
          : name === 'NotFoundError'
            ? 'No microphone was found. Connect or select a microphone and try again.'
            : 'The microphone could not start. Check your browser audio settings.',
      )
      setListeningMode(null)
      setVoicePhase('idle')
    }
  }

  function stopRecording(processAudio: boolean) {
    const recorder = recorderRef.current
    if (!recorder || recorder.state === 'inactive') return
    if (!processAudio) {
      recorder.onstop = () => cleanupRecording()
      chunksRef.current = []
    }
    recorder.stop()
  }

  function cleanupRecording() {
    streamRef.current?.getTracks().forEach(track => track.stop())
    streamRef.current = null
    recorderRef.current = null
    if (animationRef.current) cancelAnimationFrame(animationRef.current)
    animationRef.current = null
    if (maxRecordingRef.current) window.clearTimeout(maxRecordingRef.current)
    maxRecordingRef.current = null
  }

  function watchForSilence(stream: MediaStream) {
    const audioContext = new AudioContext()
    const analyser = audioContext.createAnalyser()
    analyser.fftSize = 512
    audioContext.createMediaStreamSource(stream).connect(analyser)
    const samples = new Uint8Array(analyser.fftSize)
    const startedAt = Date.now()
    let heardVoice = false
    let quietSince = 0

    const measure = () => {
      if (!recorderRef.current || recorderRef.current.state === 'inactive') {
        void audioContext.close()
        return
      }
      analyser.getByteTimeDomainData(samples)
      const rms = Math.sqrt(samples.reduce((sum, value) => {
        const normalized = (value - 128) / 128
        return sum + normalized * normalized
      }, 0) / samples.length)
      const now = Date.now()
      if (rms > 0.035) {
        heardVoice = true
        quietSince = 0
      } else if (heardVoice) {
        quietSince ||= now
        if (now - quietSince > 1100 && now - startedAt > 1400) {
          stopRecording(true)
          void audioContext.close()
          return
        }
      }
      animationRef.current = requestAnimationFrame(measure)
    }
    animationRef.current = requestAnimationFrame(measure)
  }

  async function finishDictation(blob: Blob) {
    setListeningMode(null)
    setVoicePhase('processing')
    setVoiceNotice('Transcribing your message...')
    try {
      const result = await transcribeAudio(blob)
      if (!result.transcript.trim()) throw new Error('Empty transcript')
      setInput(result.transcript.trim())
      setVoiceNotice('Dictation ready. Review the text and press send.')
    } catch {
      setVoiceNotice('The audio could not be transcribed. Check that the voice service is online.')
    } finally {
      setVoicePhase('idle')
    }
  }

  async function finishVoiceTurn(blob: Blob) {
    setListeningMode(null)
    setVoicePhase('processing')
    setVoiceNotice('The voice agent is thinking...')
    try {
      const result = await runVoiceChat(blob, convId, token)
      const transcript = result.transcript.trim()
      const answer = result.answer_text.trim()
      if (!transcript) throw new Error('Empty transcript')
      setMessages(prev => [
        ...prev,
        { role: 'user', content: transcript },
        { role: 'assistant', content: answer || 'I could not answer that voice request.' },
      ])
      if (answer) {
        await speak(answer)
      }
      if (voiceSessionRef.current) {
        setVoiceNotice('Listening for your next question...')
        await startRecording('conversation')
      }
    } catch {
      setVoiceNotice('The voice agent could not complete that turn. Press the blue button to try again.')
      endVoiceSession()
    }
  }

  async function startVoiceSession() {
    voiceSessionRef.current = true
    setVoiceSessionActive(true)
    setVoiceNotice('Listening. Speak naturally and pause when you are finished.')
    await startRecording('conversation')
  }

  function endVoiceSession() {
    voiceSessionRef.current = false
    setVoiceSessionActive(false)
    stopRecording(false)
    window.speechSynthesis?.cancel()
    setListeningMode(null)
    setVoicePhase('idle')
    setVoiceNotice('')
  }

  function speak(text: string) {
    return new Promise<void>(resolve => {
      if (!('speechSynthesis' in window)) {
        resolve()
        return
      }
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.96
      utterance.pitch = 0.94
      utterance.onstart = () => {
        setVoicePhase('speaking')
        setVoiceNotice('Voice agent is speaking...')
      }
      utterance.onend = () => resolve()
      utterance.onerror = () => resolve()
      window.speechSynthesis.speak(utterance)
    })
  }

  async function attachFile(file?: File) {
    if (!file) return
    setVoiceNotice('')
    try {
      const content = (await file.text()).slice(0, 20_000)
      setAttachment({ name: file.name, content })
    } catch {
      setVoiceNotice('That file could not be attached.')
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const isListening = listeningMode !== null

  return (
    <div className="page chat-page">
      <header className="chat-header">
        <div className="chat-heading">
          <div className="page-icon"><Sparkles className="h-5 w-5" /></div>
          <div>
            <h1>AI Assistant</h1>
            <p>Type, dictate, or start a natural voice conversation.</p>
          </div>
        </div>
        <div className="online-badge"><span className="status-dot status-dot-ready" /> Advisory mesh online</div>
      </header>

      <section className="chat-panel">
        <div className="message-list">
          <div className="message-column">
            {messages.map((message, index) => (
              <div key={index} className={`message-row ${message.role === 'user' ? 'message-row-user' : ''}`}>
                {message.role === 'assistant' && (
                  <div className="message-avatar"><Bot className="h-4 w-4" /></div>
                )}
                <div className={`message-bubble ${message.role === 'user' ? 'message-bubble-user' : ''}`}>
                  {message.content || (loading && index === messages.length - 1 ? 'Thinking...' : '')}
                </div>
                {message.role === 'user' && (
                  <div className="message-avatar message-avatar-user"><User className="h-4 w-4" /></div>
                )}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </div>

        <div className="chat-composer">
          <div className={`composer-box ${isListening ? 'composer-box-listening' : ''}`}>
            <input
              ref={fileInputRef}
              className="composer-file-input"
              type="file"
              accept=".txt,.md,.csv,.json,text/plain,text/markdown,text/csv,application/json"
              onChange={event => void attachFile(event.target.files?.[0])}
            />
            <button
              className="composer-icon-button composer-plus"
              onClick={() => fileInputRef.current?.click()}
              aria-label="Attach text file"
              title="Attach text file"
            >
              <Plus className="h-5 w-5" />
            </button>

            <div className="composer-entry">
              {attachment && (
                <div className="composer-attachment">
                  <Paperclip className="h-3 w-3" />
                  <span>{attachment.name}</span>
                  <button onClick={() => setAttachment(null)} aria-label="Remove attachment">
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
              <input
                className="composer-input"
                placeholder={isListening ? 'Listening...' : 'Ask WealthMesh anything'}
                value={input}
                onChange={event => setInput(event.target.value)}
                onKeyDown={event => {
                  if (event.key === 'Enter' && !event.shiftKey) void send()
                }}
                disabled={loading}
              />
            </div>

            <label className="composer-mode" title="Response mode">
              <select
                value={responseMode}
                onChange={event => setResponseMode(event.target.value as ResponseMode)}
                aria-label="Response mode"
              >
                <option value="instant">Instant</option>
                <option value="deep">Deep</option>
              </select>
              <ChevronDown className="h-4 w-4" />
            </label>

            <button
              className={`composer-icon-button composer-mic ${listeningMode === 'dictation' ? 'composer-control-active' : ''}`}
              onClick={() => listeningMode === 'dictation' ? stopRecording(true) : void startRecording('dictation')}
              disabled={loading || voiceSessionActive || voicePhase === 'processing'}
              aria-label={listeningMode === 'dictation' ? 'Stop dictation' : 'Dictate message'}
              title="Speech to text"
            >
              <Mic className="h-5 w-5" />
            </button>

            {voiceSessionActive ? (
              <button className="composer-stop" onClick={endVoiceSession} aria-label="End voice conversation">
                <span className="mini-wave" aria-hidden="true"><i /><i /><i /><i /></span>
                End
              </button>
            ) : input.trim() || attachment ? (
              <button
                className="composer-primary"
                onClick={() => void send()}
                disabled={loading || !input.trim()}
                aria-label="Send message"
              >
                <Send className="h-5 w-5" />
              </button>
            ) : (
              <button
                className="composer-primary composer-voice"
                onClick={() => void startVoiceSession()}
                disabled={loading || listeningMode === 'dictation' || voicePhase === 'processing'}
                aria-label="Start voice conversation"
                title="Voice to voice"
              >
                <AudioLines className="h-5 w-5" />
              </button>
            )}
          </div>
          <p className={`composer-hint ${voiceNotice ? 'composer-hint-error' : ''}`}>
            {voiceNotice || (listeningMode === 'dictation'
                ? 'Dictating only. Press the microphone again to convert your speech into text.'
                : voicePhase === 'listening'
                  ? 'Voice agent is listening and will answer aloud.'
                : 'WealthMesh can make mistakes. Verify important financial information.')}
          </p>
        </div>
      </section>
    </div>
  )
}
