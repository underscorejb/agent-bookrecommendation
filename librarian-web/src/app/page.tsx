'use client';
import { useState, useRef, useEffect } from 'react';

// 1. Updated Type to include coverUrl
type Message = {
  role: 'user' | 'agent';
  content: string;
  coverUrl?: string; // Optional property for book covers
};

export default function BookRecommendationAgent() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ genre: userMessage }),
      });
      
      const data = await res.json();
      
      // 2. Extract both text and coverUrl from your API response
      setMessages((prev) => [
        ...prev, 
        { 
          role: 'agent', 
          content: data.text || "I'm sorry, I encountered an error.",
          coverUrl: data.coverUrl // This matches the new backend service return
        }
      ]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'agent', content: "Error connecting to the librarian." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4" style={{ backgroundColor: '#F1F1F1' }}>
      <h1 className="text-3xl font-bold mb-6 text-black">📚 Book Recommendation Agent</h1>
      
      <div className="w-full max-w-2xl h-[600px] bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-4 flex flex-col"
        >
          {messages.length === 0 && (
            <p className="text-gray-400 text-center mt-10 text-lg italic">
              "Hello, what book genre do you need a recommendation for?"
            </p>
          )}
          
          {messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex gap-4 max-w-[85%] p-4 rounded-2xl text-white ${
                msg.role === 'user' 
                  ? 'self-end rounded-tr-none bg-[#004e89]' 
                  : 'self-start rounded-tl-none bg-[#00a8e8]'
              }`}
            >
              {/* 3. Render the Book Cover if it exists (Agent only) */}
              {msg.role === 'agent' && msg.coverUrl && (
                <img 
                  src={msg.coverUrl} 
                  alt="Book Cover" 
                  className="w-20 h-28 object-cover rounded shadow-md border border-white/20 flex-shrink-0 bg-gray-200"
                  onError={(e) => (e.currentTarget.style.display = 'none')} // Hide if image breaks
                />
              )}

              <div className="flex flex-col justify-center">
                <p className="leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="self-start p-4 rounded-2xl rounded-tl-none text-white animate-pulse bg-[#00a8e8]">
              Librarian is searching the archives...
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-100 flex gap-3 bg-white">
          <input 
            className="flex-1 p-3 px-5 rounded-full border border-gray-200 text-black focus:outline-none focus:ring-2 focus:ring-[#00a8e8] bg-gray-50"
            placeholder="Enter a genre..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button 
            onClick={handleSend}
            disabled={loading}
            className="px-8 py-2 rounded-full font-bold text-white transition-all active:scale-95 disabled:opacity-50"
            style={{ backgroundColor: '#ff6b35' }}
          >
            Respond
          </button>
        </div>
      </div>
    </main>
  );
}