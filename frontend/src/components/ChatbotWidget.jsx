import React, { useEffect, useRef, useState } from "react";
import { Send, X } from "lucide-react";
import { motion } from "framer-motion";

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const timeoutRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "¡Buenos días";
    if (hour < 18) return "¡Buenas tardes";
    return "¡Buenas noches";
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
        const saludo = `${getGreeting()}, soy el asistente virtual de Global Speed. ¿En qué puedo ayudarte?`;
        setMessages([{ from: "bot", text: saludo }]);
    }

    return () => clearTimeout(timeoutRef.current);
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { from: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch("http://localhost:5002/dialogflow/consulta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: userMessage.text })
      });
      const data = await response.json();
      const botMessage = { from: "bot", text: data.respuesta };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "Lo siento, ocurrió un error al procesar tu mensaje." }
      ]);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.7 }}
          className="bg-white rounded-xl shadow-2xl w-80 h-[500px] flex flex-col border border-green-600"
        >
          {/* Header */}
          <div className="bg-green-600 text-white px-4 py-3 rounded-t-xl flex items-center justify-between">
            <div className="flex items-center gap-2">
              <img src="/imagenes/logo.png" alt="Bot" className="w-7 h-7 rounded-full" />
              <span className="font-semibold">Chatbot Global Speed</span>
            </div>
            <button onClick={() => setIsOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 py-2 space-y-2 bg-gray-50">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.from === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`flex items-end max-w-[80%] ${msg.from === "user" ? "flex-row-reverse gap-2" : "gap-2"}`}>
                  <img
                    src={msg.from === "user" ? "/imagenes/perfil-none.avif" : "/imagenes/logo.png"}
                    alt="avatar"
                    className="w-6 h-6 rounded-full border"
                  />
                  <div
                    className={`px-4 py-2 rounded-xl text-sm shadow-sm whitespace-pre-wrap ${
                      msg.from === "user"
                        ? "bg-green-100 text-gray-900"
                        : "bg-white text-gray-800 border border-gray-200"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t p-2 bg-white">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-green-400 text-sm"
            />
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white p-2 rounded-full"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </motion.div>
      ) : (
        <motion.button
          onClick={() => setIsOpen(true)}
          className="bg-green-600 hover:bg-green-700 text-white w-16 h-16 p-2 rounded-full shadow-lg flex items-center justify-center animate-bounce"
        >
          <img src="/imagenes/robots.png" alt="Chatbot" className="w-full h-full rounded-full object-cover" />
        </motion.button>
      )}
    </div>
  );
};

export default ChatbotWidget;
