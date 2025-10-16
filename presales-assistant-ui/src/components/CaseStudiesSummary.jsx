import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import { getCaseStudySummary } from "../api";  // Changed from generatePitch
import ReactMarkdown from "react-markdown";
import Loader from "./Loader";

export default function CaseStudiesSummary({ customer, detectedIndustry }) {
  const [selectedIndustries, setSelectedIndustries] = useState([detectedIndustry || ""]);
  const [size, setSize] = useState("small");
  const [pitch, setPitch] = useState("");
  const [loading, setLoading] = useState(false);
  const [usedFiles, setUsedFiles] = useState([]);

  const handleGenerate = async () => {
    setLoading(true);
    setPitch("");
    setUsedFiles([]);

    try {
      const res = await getCaseStudySummary({
        customer,
        selected_industries: selectedIndustries.filter((s) => s),
        size,
      });

      setPitch(res.data.pitch_markdown || "No pitch generated");
      setUsedFiles(res.data.used_files || []);
    } catch (error) {
      console.error("Error generating pitch:", error);
      alert("Error generating pitch. Check backend.");
    }

    setLoading(false);
  };

  return (
    <Box sx={{ bgcolor: "#e3f2fd", p: 3, borderRadius: 2, mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        📚 Case Studies Summary
      </Typography>

      <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap" }}>
        <TextField
          label="Industries"
          value={selectedIndustries.join(", ")}
          onChange={(e) => setSelectedIndustries(e.target.value.split(",").map((s) => s.trim()))}
          sx={{ minWidth: 300 }}
        />
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Size</InputLabel>
          <Select value={size} onChange={(e) => setSize(e.target.value)}>
            <MenuItem value="small">Small</MenuItem>
            <MenuItem value="large">Large</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" color="primary" onClick={handleGenerate} disabled={loading}>
          GENERATE PITCH
        </Button>
      </Box>

      {loading && <Loader message="Generating case study pitch..." />}

      {pitch && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <ReactMarkdown>{pitch}</ReactMarkdown>
          {usedFiles.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption">Used files:</Typography>
              {usedFiles.map((f, idx) => (
                <Chip key={idx} label={f} size="small" sx={{ m: 0.5 }} />
              ))}
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
}