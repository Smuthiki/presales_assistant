import React, { useState } from "react";
import { Box, Typography, Button, TextField, Paper } from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import { chatWithAssistant } from "../api";
import ReactMarkdown from "react-markdown";
import Loader from "./Loader";

export default function ChatSection({ customer, industry }) {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [webResults, setWebResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    const res = await chatWithAssistant({
      customer,
      selected_industries: [industry],
      selected_techs: [],
      message,
      history: [],
      use_web: true,
      use_cases: true,
    });
    setReply(res.data.reply);
    setWebResults(res.data.web_refs || []);
    setLoading(false);
  };

  return (
    <Box sx={{ bgcolor: "#e1f5fe", p: 3, borderRadius: 2, mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        <ChatIcon /> 💬 Chat Assistant
      </Typography>
      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <TextField
          label="Ask Presales Assistant"
          value={message}
          onChange={e => setMessage(e.target.value)}
          fullWidth
        />
        <Button variant="contained" color="primary" onClick={handleSend} disabled={loading}>
          {loading ? <Loader /> : "Send"}
        </Button>
      </Box>
      {loading && <Loader />}
      {webResults.length > 0 && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: "#fffde7", border: "1px solid #fbc02d" }}>
          <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>🌐 Web Results (SerpAPI):</Typography>
          <ul>
            {webResults.map((w, idx) => (
              <li key={idx}>
                <a href={w.link} target="_blank" rel="noopener noreferrer">{w.title}</a>
                <br />
                <span style={{ color: "#666" }}>{w.snippet}</span>
              </li>
            ))}
          </ul>
        </Paper>
      )}
      {reply && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>🤖 Presales Assistant Answer:</Typography>
          <ReactMarkdown>{reply}</ReactMarkdown>
        </Paper>
      )}
    </Box>
  );
}