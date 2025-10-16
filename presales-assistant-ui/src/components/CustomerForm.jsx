import React, { useState } from "react";
import { TextField, Button, Box, Typography } from "@mui/material";
import { determineIndustry } from "../api";
import SearchIcon from "@mui/icons-material/Search";

export default function CustomerForm({ onIndustryDetermined }) {
  const [customer, setCustomer] = useState("");
  const [loading, setLoading] = useState(false);
  const [industry, setIndustry] = useState("");
  const [confidence, setConfidence] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const res = await determineIndustry(customer);
      
      // FIX: Handle direct response (not nested in .data)
      const industryData = res.industry || res.data?.industry || "Unknown";
      const confidenceData = res.confidence || res.data?.confidence || 0.8;
      
      console.log("[CustomerForm] API Response:", res);
      console.log("[CustomerForm] Extracted industry:", industryData);
      
      setIndustry(industryData);
      setConfidence(confidenceData);
      
      onIndustryDetermined(customer, industryData);
    } catch (error) {
      console.error("[CustomerForm] Error:", error);
      alert("Error detecting industry. Please try again.");
      setIndustry("Unknown");
      setConfidence(0);
    }
    
    setLoading(false);
  };

  return (
    <Box sx={{ bgcolor: "#f5f5f5", p: 3, borderRadius: 2, mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        <SearchIcon /> Enter Customer Name
      </Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Customer / Company"
          value={customer}
          onChange={(e) => setCustomer(e.target.value)}
          required
          sx={{ mr: 2, width: "300px" }}
        />
        <Button type="submit" variant="contained" color="primary" disabled={loading}>
          {loading ? "Detecting..." : "Detect Industry"}
        </Button>
      </form>
      {industry && (
        <Typography sx={{ mt: 2 }}>
          <strong>Guessed Industry:</strong> {industry} ({Math.round(confidence * 100)}%)
        </Typography>
      )}
    </Box>
  );
}